#!/bin/sh
# Checks the extension's proofs and encodings; does not rerun the open searches.
set -e
cd "$(dirname "$0")"
python3 profile_transfer.py
python3 bound_closure.py --limit 128
if [ ! -x .venv/bin/python ]; then
    echo 'python-sat venv missing: combinatorial checks passed, SAT checks not run'
    exit 0
fi
.venv/bin/python sentinel_validate.py
extension_check_dir=$(mktemp -d "${TMPDIR:-/tmp}/sorting-extension.XXXXXX")
for extension_check_pair in 5-4 7-5 9-6 11-7; do
    extension_check_n=${extension_check_pair%-*}
    extension_check_d=${extension_check_pair#*-}
    .venv/bin/python sentinel_cegar.py \
        --replay "../results/sentinel-d${extension_check_n}-d${extension_check_d}.json" \
        --out "$extension_check_dir/$extension_check_pair.json" --seconds 120
done
python3 - "$extension_check_dir" <<'PY'
import json
from pathlib import Path
import sys
paths = list(Path(sys.argv[1]).glob('*.json'))
assert len(paths) == 4
for path in paths:
    record = json.loads(path.read_text())
    assert record['status'] == 'UNSAT', (path.name, record['status'])
print('all four recorded lower-bound instances replayed as UNSAT')
PY
echo "Replay outputs: $extension_check_dir"
