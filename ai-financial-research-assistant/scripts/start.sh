#!/usr/bin/env bash
# Local launcher: does not install software, read .env, or save contact information.
set -euo pipefail
cd "$(dirname "$0")/.."
finsight_python="$PWD/.venv/bin/python"
if [[ ! -x "$finsight_python" ]]; then
  echo 'Virtual environment missing. Follow docs/mac-setup.md (create .venv and install requirements).'
  exit 1
fi
if ! "$finsight_python" -c 'import sys; assert sys.version_info[:2] == (3, 12); import streamlit, finsight' 2>/dev/null; then
  echo 'FinSight needs Python 3.12 and its project dependencies. Follow docs/mac-setup.md.'
  exit 1
fi
if [[ -z "${SEC_USER_AGENT:-}" && -t 0 ]]; then
  read -r -p 'SEC contact email (Enter to use the offline example only): ' finsight_contact
  if [[ -n "$finsight_contact" ]]; then
    export SEC_USER_AGENT="FinSightAI $finsight_contact"
  fi
fi
if [[ -n "${SEC_USER_AGENT:-}" ]]; then
  "$finsight_python" -c 'from finsight.sec import SECClient, SECError
try:
    SECClient()
except SECError as exc:
    raise SystemExit(str(exc))'
else
  echo 'SEC identification is unset. Use Synthetic example or Upload CSV.'
fi
exec "$finsight_python" -m streamlit run app/main.py --server.address 127.0.0.1 "$@"
