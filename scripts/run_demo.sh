#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
if [[ -f /usr/local/birensupa/br_container_tools/brsw_set_env.sh ]]; then
  source /usr/local/birensupa/br_container_tools/brsw_set_env.sh >/dev/null 2>&1
fi
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
python3 -m quantaforge.web --host 0.0.0.0 --port "${QUANTAFORGE_PORT:-7860}"
