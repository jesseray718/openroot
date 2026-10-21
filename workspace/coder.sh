#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/openloom-build/workspace"
source "$HOME/openloom-build/.venv/bin/activate"

export OPENLOOM_WORKSPACE="$PWD"
export OPENLOOM_PODS="$PWD/pods"
export OPENLOOM_RAG_DB="$HOME/openloom-build/grand-unification/unified_rag.sqlite3"
export OPENLOOM_MODEL_ACCESS="$HOME/openloom-build/pods/model-access/model_access_catalog.json"

exec bash
