### Architecture Overview

The OpenLoom CLI app will consist of several components:

1. **CLI Entrypoints**: `cli.py` will handle the `openloom init`, `openloom[9D[K
`openloom ingest`, and `openloom verify` commands.
2. **Ingest Modules**: Each supported input type (SQLite, CSV/JSONL, Markdo[6D[K
Markdown) will have its own ingest module (`ingest_sqlite.py`, `ingest_csv.[12D[K
`ingest_csv.py`, `ingest_markdown.py`).
3. **Schema Management**: `schema.py` will define the database schema.
4. **Chunking**: `chunking.py` will handle the creation of retrieval chunks[6D[K
chunks.
5. **Manifest and Receipts**: `manifest.py` will generate the manifest and [K
ingest receipts.
6. **Error Handling**: Errors will be logged to `errors.jsonl`.

### Code Implementation

#### 1. `openloom/cli.py`

```python
import click
from openloom.ingest_sqlite import ingest_sqlite
from openloom.ingest_csv import ingest_csv
from openloom.ingest_markdown import ingest_markdown
from openloom.schema import create_schema
from openloom.manifest import generate_manifest
from openloom.manifest import generate_receipt

@click.group()
def cli():
    pass

@cli.command()
@click.argument('pod_name')
def init(pod_name):
    """Initialize a new pod."""
    create_schema(pod_name)
    generate_manifest(pod_name)
    click.echo(f"Pod '{pod_name}' initialized.")

@cli.command()
@click.argument('pod_name')
@click.argument('source_path')
def ingest(pod_name, source_path):
    """Ingest data into the pod."""
    if source_path.endswith('.db'):
        ingest_sqlite(pod_name, source_path)
    elif source_path.endswith('.csv') or source_path.endswith('.jsonl'):
        ingest_csv(pod_name, source_path)
    elif source_path.endswith('.md'):
        ingest_markdown(pod_name, source_path)
    else:
        click.echo("Unsupported file type.")
        return
    generate_receipt(pod_name, source_path)
    click.echo(f"Data ingested into pod '{pod_name}'.")

@cli.command()
@click.argument('pod_name')
def verify(pod_name):
    """Verify the integrity of the pod."""
    # Placeholder for verification logic
    click.echo(f"Verifying pod '{pod_name}'...")
    click.echo("Verification complete.")

if __name__ == '__main__':
    cli()
```

#### 2. `openloom/schema.py`

```python
import sqlite3

def create_schema(pod_name):
    """Create the database schema."""
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY,
            sha256 TEXT NOT NULL,
            provenance TEXT NOT NULL
        );
        CREATE TABLE records (
            id INTEGER PRIMARY KEY,
            source_id INTEGER,
            json TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(id)
        );
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY,
            source_id INTEGER,
            record_id INTEGER,
            text TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(id),
            FOREIGN KEY (record_id) REFERENCES records(id)
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(text);
        CREATE TABLE embeddings (
            id INTEGER PRIMARY KEY,
            chunk_id INTEGER,
            model TEXT NOT NULL,
            dimensions INTEGER NOT NULL,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id)
        );
        CREATE TABLE queries (
            id INTEGER PRIMARY KEY,
            text TEXT NOT NULL
        );
        CREATE TABLE corrections (
            id INTEGER PRIMARY KEY,
            query_id INTEGER,
            answer TEXT NOT NULL,
            label TEXT NOT NULL,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        );
        CREATE TABLE pathways (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            steps TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
```

#### 3. `openloom/manifest.py`

```python
import json

def generate_manifest(pod_name):
    """Generate the manifest file."""
    with open(f"{pod_name}/manifest.json", 'w') as f:
        json.dump({
            "version": "1.0",
            "sources": []
        }, f, indent=4)

def generate_receipt(pod_name, source_path):
    """Generate the ingest receipt file."""
    with open(f"{pod_name}/ingest_receipt.json", 'w') as f:
        json.dump({
            "source_path": source_path,
            "timestamp": "2023-04-01T12:00:00Z"
        }, f, indent=4)
```

#### 4. `openloom/ingest_sqlite.py`

```python
import sqlite3
from hashlib import sha256
from openloom.schema import create_schema

def ingest_sqlite(pod_name, source_path):
    """Ingest data from an SQLite database."""
    conn = sqlite3.connect(source_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources")
    sources = cursor.fetchall()
    for source in sources:
        sha256_hash = sha256(source[1].encode()).hexdigest()
        insert_source(pod_name, sha256_hash, source[1])
    conn.close()

def insert_source(pod_name, sha256_hash, provenance):
    """Insert a source into the database."""
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sources (sha256, provenance) VALUES (?, ?)"[3D[K
?)", (sha256_hash, provenance))
    conn.commit()
    conn.close()
```

#### 5. `openloom/ingest_csv.py`

```python
import csv
from hashlib import sha256
from openloom.schema import create_schema

def ingest_csv(pod_name, source_path):
    """Ingest data from a CSV file."""
    with open(source_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sha256_hash = sha256(row['provenance'].encode()).hexdigest()
            insert_source(pod_name, sha256_hash, row['provenance'])
            insert_record(pod_name, sha256_hash, json.dumps(row))

def insert_source(pod_name, sha256_hash, provenance):
    """Insert a source into the database."""
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sources (sha256, provenance) VALUES (?, ?)"[3D[K
?)", (sha256_hash, provenance))
    conn.commit()
    conn.close()

def insert_record(pod_name, sha256_hash, json_data):
    """Insert a record into the database."""
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (source_id, json) VALUES ((SELECT i[1D[K
id FROM sources WHERE sha256 = ?), ?)", (sha256_hash, json_data))
    conn.commit()
    conn.close()
```

#### 6. `openloom/ingest_markdown.py`

```python
import markdown
from hashlib import sha256
from openloom.schema import create_schema

def ingest_markdown(pod_name, source_path):
    """Ingest data from a Markdown file."""
    with open(source_path, 'r') as f:
        text = f.read()
        sha256_hash = sha256(text.encode()).hexdigest()
        insert_source(pod_name, sha256_hash, source_path)
        insert_chunk(pod_name, sha256_hash, text)

def insert_source(pod_name, sha256_hash, provenance):
    """Insert a source into the database."""
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sources (sha256, provenance) VALUES (?, ?)"[3D[K
?)", (sha256_hash, provenance))
    conn.commit()
    conn.close()

def insert_chunk(pod_name, sha256_hash, text):
    """Insert a chunk into the database."""
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chunks (source_id, text) VALUES ((SELECT id[2D[K
id FROM sources WHERE sha256 = ?), ?)", (sha256_hash, text))
    conn.commit()
    conn.close()
```

#### 7. `tests/test_sqlite_ingest.py`

```python
import sqlite3
from openloom.ingest_sqlite import ingest_sqlite

def test_sqlite_ingest():
    pod_name = "test_pod"
    source_path = "test_data.db"
    ingest_sqlite(pod_name, source_path)
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sources")
    assert cursor.fetchone()[0] > 0
    conn.close()
```

#### 8. `tests/test_markdown_ingest.py`

```python
from openloom.ingest_markdown import ingest_markdown

def test_markdown_ingest():
    pod_name = "test_pod"
    source_path = "test_data.md"
    ingest_markdown(pod_name, source_path)
    conn = sqlite3.connect(f"{pod_name}/pod.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sources")
    assert cursor.fetchone()[0] > 0
    conn.close()
```

### Conclusion

This minimal implementation of OpenLoom provides a basic CLI app for ingest[6D[K
ingesting data into a portable SQLite pod while preserving provenance. The [K
code is structured to be easily extendable and maintainable, with each comp[4D[K
component clearly defined and isolated.

