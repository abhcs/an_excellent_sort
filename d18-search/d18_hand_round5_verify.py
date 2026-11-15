#!/usr/bin/env python3
"""Fresh whole-family cut6 replay of the three round5 combined survivors."""
import json
from pathlib import Path
import subprocess
import time

from d18_hand_next_reschedule import digest, save

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'


def main():
    started = time.monotonic()
    binary = Path('/private/tmp/d18_hand_round5_reschedule_states')
    subprocess.run(['c++', '-O3', '-std=c++17', str(HERE / 'd18_hand_round5_reschedule_states.cpp'),
                    '-o', str(binary)], check=True, capture_output=True, timeout=20)
    component_binary = Path('/private/tmp/d18_hand_round5_component_states')
    records = []
    for name in ('beam00', 'beam16', 'beam32'):
        source = OUT / f'd18_hand_round5_combined-{name}.json'
        result_path = source.with_name(source.stem + '-result.json')
        data = json.loads(source.read_text())
        result = json.loads(result_path.read_text())
        assert result['status'] == 'SURVIVOR'
        assert result['input_sha256'] == digest(source)
        prefix = data['prefix'] + [result['layer6']]
        lines = ['18 6']
        for layer in prefix:
            row = [-1] * 18
            for a, b in layer:
                assert 0 <= a < b < 18 and row[a] == row[b] == -1
                row[a], row[b] = b, a
            lines.append(' '.join(map(str, row)))
        mates = OUT / f'd18_hand_round5_combined-{name}-cut6.txt'
        mates.write_text('\n'.join(lines) + '\n')
        collections = []
        for r in (7, 8, 9):
            command = ([str(binary), str(mates), str(r), '1'] if r < 9 else
                       [str(component_binary), str(mates), 'three', 'all'])
            call_started = time.monotonic()
            call = subprocess.run(command, capture_output=True, text=True, timeout=20)
            assert call.returncode == 0, call.stderr
            collection = json.loads(call.stdout)
            assert collection['accepted_placements'] == 0
            collection.update(terminal='EXITED', returncode=0, wall_cap_seconds=20,
                              seconds=time.monotonic() - call_started)
            collections.append(collection)
        records.append(dict(case=name, status='VERIFIED', layer6=result['layer6'],
                            full_cut6_collections=collections, input_sha256=digest(source),
                            result_sha256=digest(result_path)))
    report = dict(status='VERIFIED', records=records, seconds=time.monotonic() - started,
                  uses_sat=False, source_sha256=digest(Path(__file__)),
                  rescheduling_collector_sha256=digest(HERE / 'd18_hand_round5_reschedule_states.cpp'),
                  component_collector_sha256=digest(HERE / 'merge_component_states.cpp'))
    save(OUT / 'd18_hand_round5_combined-verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
