#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read-only inventory of likely local embedding databases."""

import datetime
from contextlib import closing
import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path


HOME = Path("/home/jesse")
UNIFIED_DATABASE = (
    HOME
    / "recovery-evidence"
    / "unified-evidence-800k-v3-20261014T230900Z"
    / "unified_evidence.db"
)
REPORT_ROOT = HOME / "recovery-evidence"
SEARCH_DIRS = ("openroot", "pods", "recovery-evidence")
DATABASE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
EXCLUDED_DIRS = {
    ".git",
    ".cache",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "models",
    "model",
    "backups",
    "backup",
    "private",
    "secrets",
    "credentials",
}
EXCLUDED_NAME = re.compile(
    r"(?:^|[._-])(backup|backups|private|secret|secrets|credential|credentials|"
    r"password|token|wal|shm)(?:$|[._-])",
    re.IGNORECASE,
)
MODEL_COLUMNS = ("model", "embedding_model", "model_name")
DIMENSION_COLUMNS = ("dim", "dimension", "dimensions", "embedding_dim")
VECTOR_COLUMNS = ("embedding", "embedding_json", "vector", "vector_json", "vec")
HASH_COLUMNS = (
    "chunk_content_sha256",
    "content_sha256",
    "chunk_sha256",
    "text_sha256",
    "chunk_hash",
    "content_hash",
    "row_sha",
)
TEXT_COLUMNS = ("chunk_text", "text", "content", "body", "chunk")
ARTIFACT_HASH_COLUMNS = (
    "source_artifact_sha256",
    "artifact_sha256",
    "source_sha256",
    "file_sha256",
)
PATH_COLUMNS = ("source_path", "file_path", "path", "uri")
SOURCE_ID_COLUMNS = ("source_id", "source_key", "artifact_id")
CHUNK_ID_COLUMNS = ("chunk_id", "chunk_key", "id")


def quote_identifier(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def open_read_only(path):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    return closing(sqlite3.connect(uri, uri=True))


def tables_and_columns(connection):
    tables = {}
    rows = connection.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type = 'table' ORDER BY name"
    )
    for name, create_sql in rows:
        columns = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(" + quote_identifier(name) + ")"
            )
        ]
        tables[name] = {"create_sql": create_sql, "columns": columns}
    return tables


def find_column(columns, aliases):
    by_lower = {column.lower(): column for column in columns}
    return next((by_lower[name] for name in aliases if name in by_lower), None)


def find_vector_column(columns):
    column = find_column(columns, VECTOR_COLUMNS)
    if column:
        return column
    return next(
        (name for name in columns if "embedding" in name.lower() or "vector" in name.lower()),
        None,
    )


def looks_like_vector_database(tables):
    for table_name, schema in tables.items():
        text = " ".join((table_name, *schema["columns"])).lower()
        if "embedding" in text or "vector" in text:
            return True
    return False


def is_safe_database_path(path):
    if path.suffix.lower() not in DATABASE_SUFFIXES:
        return False
    if EXCLUDED_NAME.search(path.name):
        return False
    if any(EXCLUDED_NAME.search(part) for part in path.parts):
        return False
    return True


def iter_database_files(home):
    for dirname in SEARCH_DIRS:
        start = home / dirname
        if not start.is_dir() or start.is_symlink():
            continue
        for current, directories, filenames in os.walk(start, followlinks=False):
            directories[:] = sorted(
                name
                for name in directories
                if name.lower() not in EXCLUDED_DIRS
                and not name.startswith(".")
                and not EXCLUDED_NAME.search(name)
                and not (Path(current) / name).is_symlink()
                and not (Path(current) / name / ".git").exists()
            )
            for filename in sorted(filenames):
                path = Path(current) / filename
                if not path.is_symlink() and is_safe_database_path(path):
                    yield path


def nonempty_clause(column):
    quoted = quote_identifier(column)
    return f"{quoted} IS NOT NULL AND TRIM(CAST({quoted} AS TEXT)) != ''"


def count_nonempty(connection, table, columns):
    if not columns:
        return 0
    conditions = " AND ".join(nonempty_clause(column) for column in columns)
    return connection.execute(
        f"SELECT COUNT(*) FROM {quote_identifier(table)} WHERE {conditions}"
    ).fetchone()[0]


def is_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def json_vector_dimensions(connection, table, column):
    dimensions = set()
    valid_vectors = 0
    query = (
        f"SELECT {quote_identifier(column)} FROM {quote_identifier(table)} "
        f"WHERE {quote_identifier(column)} IS NOT NULL"
    )
    for (value,) in connection.execute(query):
        if not isinstance(value, str):
            continue
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            continue
        if isinstance(decoded, list):
            dimensions.add(len(decoded))
            valid_vectors += 1
    return sorted(dimensions), valid_vectors


def value_set(connection, table, column):
    query = (
        f"SELECT DISTINCT {quote_identifier(column)} "
        f"FROM {quote_identifier(table)} WHERE {quote_identifier(column)} IS NOT NULL "
        "ORDER BY 1"
    )
    return [row[0] for row in connection.execute(query)]


def schema_record(connection, tables):
    result = {}
    for name, schema in tables.items():
        result[name] = {
            "create_table_sql": schema["create_sql"],
            "columns": schema["columns"],
            "row_count": connection.execute(
                f"SELECT COUNT(*) FROM {quote_identifier(name)}"
            ).fetchone()[0],
        }
    return result


def unified_schema(path):
    if not path.is_file():
        return {"database_path": str(path), "available": False, "tables": {}}
    try:
        with open_read_only(path) as connection:
            tables = tables_and_columns(connection)
            expected = {}
            for name in ("sources", "rag_chunks", "embeddings"):
                item = tables.get(name)
                expected[name] = (
                    {
                        "present": True,
                        "create_table_sql": item["create_sql"],
                        "columns": item["columns"],
                    }
                    if item
                    else {"present": False, "create_table_sql": None, "columns": []}
                )
            return {
                "database_path": str(path),
                "available": True,
                "tables": expected,
            }
    except sqlite3.Error as error:
        return {
            "database_path": str(path),
            "available": False,
            "error": type(error).__name__,
            "tables": {},
        }


def assess_mapping(connection, tables, embedding_table, embedding_count):
    vector_schema = tables[embedding_table]
    vector_columns = vector_schema["columns"]
    hash_column = find_column(vector_columns, HASH_COLUMNS)
    text_column = find_column(vector_columns, TEXT_COLUMNS)
    artifact_column = find_column(vector_columns, ARTIFACT_HASH_COLUMNS)
    path_column = find_column(vector_columns, PATH_COLUMNS)
    complete = 0
    field_counts = {}
    mapping_query = None

    if hash_column and text_column and artifact_column and path_column:
        complete_columns = [
            hash_column,
            text_column,
            artifact_column,
            path_column,
        ]
        complete_where = " AND ".join(nonempty_clause(column) for column in complete_columns)
        mapping_query = (
            f"SELECT {', '.join(quote_identifier(column) for column in complete_columns)} "
            f"FROM {quote_identifier(embedding_table)} WHERE {complete_where}"
        )
    for key, column in (
        ("chunk_content_sha256", hash_column),
        ("chunk_text", text_column),
        ("source_artifact_sha256", artifact_column),
        ("source_path", path_column),
    ):
        field_counts[key] = (
            count_nonempty(connection, embedding_table, [column]) if column else 0
        )
    else:
        chunk_table = None
        chunk_hash = None
        chunk_text = None
        join = None
        for candidate, schema in tables.items():
            if candidate == embedding_table:
                continue
            candidate_hash = find_column(schema["columns"], HASH_COLUMNS)
            candidate_text = find_column(schema["columns"], TEXT_COLUMNS)
            if not candidate_hash or not candidate_text:
                continue
            link = None
            if hash_column:
                link = (hash_column, candidate_hash)
            else:
                vector_id = find_column(vector_columns, CHUNK_ID_COLUMNS)
                chunk_id = find_column(schema["columns"], CHUNK_ID_COLUMNS)
                if vector_id and chunk_id:
                    link = (vector_id, chunk_id)
            if link:
                chunk_table = candidate
                chunk_hash = candidate_hash
                chunk_text = candidate_text
                join = (
                    f"{quote_identifier(embedding_table)} AS e JOIN "
                    f"{quote_identifier(chunk_table)} AS c ON "
                    f"e.{quote_identifier(link[0])} = c.{quote_identifier(link[1])}"
                )
                break

        if chunk_table:
            chunk_schema = tables[chunk_table]
            chunk_artifact = find_column(
                chunk_schema["columns"], ARTIFACT_HASH_COLUMNS
            )
            chunk_path = find_column(chunk_schema["columns"], PATH_COLUMNS)
            source_table = None
            source_artifact = None
            source_path = None
            source_join = None
            if not (chunk_artifact and chunk_path):
                chunk_source_id = find_column(
                    chunk_schema["columns"], SOURCE_ID_COLUMNS
                )
                for candidate, schema in tables.items():
                    if candidate in (embedding_table, chunk_table):
                        continue
                    candidate_artifact = find_column(
                        schema["columns"], ARTIFACT_HASH_COLUMNS
                    )
                    candidate_path = find_column(schema["columns"], PATH_COLUMNS)
                    source_id = find_column(schema["columns"], SOURCE_ID_COLUMNS + ("id",))
                    if chunk_source_id and source_id and candidate_artifact and candidate_path:
                        source_table = candidate
                        source_artifact = candidate_artifact
                        source_path = candidate_path
                        source_join = (
                            f" JOIN {quote_identifier(source_table)} AS s ON "
                            f"c.{quote_identifier(chunk_source_id)} = "
                            f"s.{quote_identifier(source_id)}"
                        )
                        break
            if chunk_artifact and chunk_path:
                artifact_expr = f"c.{quote_identifier(chunk_artifact)}"
                path_expr = f"c.{quote_identifier(chunk_path)}"
            elif source_join:
                artifact_expr = f"s.{quote_identifier(source_artifact)}"
                path_expr = f"s.{quote_identifier(source_path)}"
                join += source_join
            else:
                artifact_expr = path_expr = None

            if artifact_expr and path_expr:
                conditions = [
                    f"c.{quote_identifier(chunk_hash)} IS NOT NULL",
                    f"CAST(c.{quote_identifier(chunk_hash)} AS TEXT) != ''",
                    f"c.{quote_identifier(chunk_text)} IS NOT NULL",
                    f"CAST(c.{quote_identifier(chunk_text)} AS TEXT) != ''",
                    f"{artifact_expr} IS NOT NULL",
                    f"CAST({artifact_expr} AS TEXT) != ''",
                    f"{path_expr} IS NOT NULL",
                    f"CAST({path_expr} AS TEXT) != ''",
                ]
                mapping_query = (
                    f"SELECT c.{quote_identifier(chunk_hash)}, "
                    f"c.{quote_identifier(chunk_text)}, {artifact_expr}, {path_expr} "
                    f"FROM {join} WHERE " + " AND ".join(conditions)
                )

    complete = verified_hashes = verified_artifacts = 0
    if mapping_query:
        for chunk_hash_value, text, artifact_hash, source_path in connection.execute(
            mapping_query
        ):
            complete += 1
            text_value = (
                text.decode("utf-8", errors="replace")
                if isinstance(text, bytes)
                else str(text)
            )
            if (
                is_sha256(chunk_hash_value)
                and hashlib.sha256(text_value.encode("utf-8")).hexdigest()
                == chunk_hash_value.lower()
            ):
                verified_hashes += 1
            if is_sha256(artifact_hash):
                verified_artifacts += 1
    mapped = complete > 0
    return {
        "chunk_content_sha256_recoverable": verified_hashes == embedding_count
        and embedding_count > 0,
        "chunk_text_present": bool(field_counts["chunk_text"] or mapped),
        "source_artifact_sha256_recoverable": verified_artifacts == embedding_count
        and embedding_count > 0,
        "source_path_recoverable": bool(field_counts["source_path"] or mapped),
        "source_provenance_recoverable": bool(
            embedding_count > 0
            and complete == embedding_count
            and verified_artifacts == embedding_count
        ),
        "vectors_with_complete_mapping": complete,
        "vectors_with_verified_chunk_hash": verified_hashes,
        "vectors_with_verified_artifact_sha256": verified_artifacts,
        "vectors_total": embedding_count,
    }


def inspect_database(path, unified):
    record = {"database_path": str(path)}
    try:
        with open_read_only(path) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            tables = tables_and_columns(connection)
            if not looks_like_vector_database(tables):
                return None
            record.update(
                {
                    "integrity_check": integrity,
                    "tables": schema_record(connection, tables),
                }
            )
            vector_tables = [
                (name, schema)
                for name, schema in tables.items()
                if find_vector_column(schema["columns"])
                or "embedding" in name.lower()
                or "vector" in name.lower()
            ]
            if not vector_tables:
                record.update(
                    {
                        "embedding_models": [],
                        "embedding_dimensions": [],
                        "chunk_content_sha256_recoverable": False,
                        "chunk_text_present": False,
                        "source_artifact_sha256_recoverable": False,
                        "source_path_recoverable": False,
                        "source_provenance_recoverable": False,
                        "vectors_with_verified_chunk_hash": 0,
                        "vectors_with_verified_artifact_sha256": 0,
                        "compatible_with_unified_embeddings_table": False,
                        "recommended_merge_strategy": "DO_NOT_MERGE",
                    }
                )
                return record

            mapping_results = []
            models = set()
            dimensions = set()
            embeddings_count = 0
            metadata_complete = True
            destination = unified["tables"].get("embeddings", {})
            destination_columns = {c.lower() for c in destination.get("columns", [])}
            for table_name, schema in vector_tables:
                columns = schema["columns"]
                row_count = connection.execute(
                    f"SELECT COUNT(*) FROM {quote_identifier(table_name)}"
                ).fetchone()[0]
                embeddings_count += row_count
                model_column = find_column(columns, MODEL_COLUMNS)
                dimension_column = find_column(columns, DIMENSION_COLUMNS)
                vector_column = find_vector_column(columns)
                if model_column:
                    models.update(value_set(connection, table_name, model_column))
                    metadata_complete = metadata_complete and (
                        count_nonempty(connection, table_name, [model_column]) == row_count
                    )
                else:
                    metadata_complete = False
                if dimension_column:
                    dimensions.update(
                        value_set(connection, table_name, dimension_column)
                    )
                    metadata_complete = metadata_complete and (
                        count_nonempty(connection, table_name, [dimension_column])
                        == row_count
                    )
                elif vector_column:
                    inferred_dimensions, valid_vectors = json_vector_dimensions(
                        connection, table_name, vector_column
                    )
                    dimensions.update(inferred_dimensions)
                    metadata_complete = metadata_complete and valid_vectors == row_count
                else:
                    metadata_complete = False
                mapping_results.append(
                    assess_mapping(connection, tables, table_name, row_count)
                )

            mapping_counts = {
                name: sum(item[name] for item in mapping_results)
                for name in (
                    "vectors_with_complete_mapping",
                    "vectors_with_verified_chunk_hash",
                    "vectors_with_verified_artifact_sha256",
                    "vectors_total",
                )
            }
            has_mapping = bool(mapping_results) and all(
                item["source_provenance_recoverable"] for item in mapping_results
            )
            all_models_match = bool(models) and all(
                str(model) == "nomic-embed-text" for model in models
            )
            all_dimensions_match = bool(dimensions) and all(
                str(dimension) == "768" for dimension in dimensions
            )
            no_model_conflicts = all(
                str(model) == "nomic-embed-text" for model in models
            )
            no_dimension_conflicts = all(
                str(dimension) == "768" for dimension in dimensions
            )
            vector_fields = any(
                name in destination_columns
                for name in ("embedding", "vector", "vec", "embedding_json", "vector_json")
            )
            model_fields = any(
                name in destination_columns for name in MODEL_COLUMNS
            )
            dimension_fields = any(
                name in destination_columns for name in DIMENSION_COLUMNS
            )
            hash_fields = any(
                name in destination_columns for name in HASH_COLUMNS
            )
            compatible = bool(
                unified.get("available")
                and destination.get("present")
                and unified["tables"]["sources"]["present"]
                and unified["tables"]["rag_chunks"]["present"]
                and vector_fields
                and model_fields
                and dimension_fields
                and hash_fields
                and all(find_vector_column(tables[name]["columns"]) for name, _ in vector_tables)
            )
            safe = (
                compatible
                and all_models_match
                and all_dimensions_match
                and metadata_complete
                and has_mapping
                and mapping_counts["vectors_with_verified_chunk_hash"]
                == mapping_counts["vectors_total"]
                and mapping_counts["vectors_total"] > 0
                and integrity == "ok"
            )
            if safe:
                strategy = "SAFE_MERGE"
            elif (
                compatible
                and integrity == "ok"
                and mapping_counts["vectors_total"] > 0
                and no_model_conflicts
                and no_dimension_conflicts
                and mapping_counts["vectors_with_complete_mapping"] > 0
                and mapping_counts["vectors_with_verified_chunk_hash"]
                == mapping_counts["vectors_with_complete_mapping"]
                and mapping_counts["vectors_with_verified_artifact_sha256"]
                == mapping_counts["vectors_with_complete_mapping"]
            ):
                strategy = "CONDITIONAL_MERGE"
            else:
                strategy = "DO_NOT_MERGE"

            record.update(
                {
                    "embedding_models": sorted(models, key=str),
                    "embedding_dimensions": sorted(dimensions, key=str),
                    "chunk_content_sha256_recoverable": all(
                        item["chunk_content_sha256_recoverable"]
                        for item in mapping_results
                    ),
                    "chunk_text_present": all(
                        item["chunk_text_present"] for item in mapping_results
                    ),
                    "source_artifact_sha256_recoverable": all(
                        item["source_artifact_sha256_recoverable"]
                        for item in mapping_results
                    ),
                    "source_path_recoverable": all(
                        item["source_path_recoverable"] for item in mapping_results
                    ),
                    "source_provenance_recoverable": has_mapping,
                    "vectors_with_complete_mapping": mapping_counts[
                        "vectors_with_complete_mapping"
                    ],
                    "vectors_with_verified_chunk_hash": mapping_counts[
                        "vectors_with_verified_chunk_hash"
                    ],
                    "vectors_with_verified_artifact_sha256": mapping_counts[
                        "vectors_with_verified_artifact_sha256"
                    ],
                    "vectors_total": mapping_counts["vectors_total"],
                    "compatible_with_unified_embeddings_table": compatible,
                    "recommended_merge_strategy": strategy,
                }
            )
            return record
    except (sqlite3.Error, OSError, ValueError) as error:
        record["inspection_error"] = type(error).__name__
        return record


def build_report(home=HOME, unified_path=UNIFIED_DATABASE):
    unified = unified_schema(Path(unified_path))
    databases = []
    excluded = Path(unified_path).resolve()
    for path in iter_database_files(Path(home)):
        try:
            if path.resolve() == excluded:
                continue
        except OSError:
            continue
        result = inspect_database(path, unified)
        if result is not None:
            databases.append(result)
    return {
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "unified_database": unified,
        "candidate_databases": databases,
        "merge_performed": False,
    }


def write_report(report, report_root=REPORT_ROOT):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = Path(report_root) / f"vector-inventory-{stamp}"
    suffix = 1
    while True:
        try:
            directory.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            directory = Path(report_root) / f"vector-inventory-{stamp}-{suffix:02d}"
            suffix += 1
    report_path = directory / "vector_inventory.json"
    with report_path.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2, sort_keys=True)
        output.write("\n")
    return report_path


def main(home=HOME, unified_path=UNIFIED_DATABASE, report_root=REPORT_ROOT):
    report = build_report(home, unified_path)
    report_path = write_report(report, report_root)
    candidates = report["candidate_databases"]
    counts = {
        strategy: sum(
            item.get("recommended_merge_strategy") == strategy for item in candidates
        )
        for strategy in ("SAFE_MERGE", "CONDITIONAL_MERGE", "DO_NOT_MERGE")
    }
    print(f"Report: {report_path}")
    print(
        "Compatibility: "
        f"{len(candidates)} candidate(s); "
        f"{counts['SAFE_MERGE']} safe, "
        f"{counts['CONDITIONAL_MERGE']} conditional, "
        f"{counts['DO_NOT_MERGE']} do not merge."
    )


if __name__ == "__main__":
    main()
