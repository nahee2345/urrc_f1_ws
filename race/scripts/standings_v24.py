#!/usr/bin/env python3
"""Read-only official stage standings. Does not infer missing teams or certify provisional ranks."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

STAGES = ('qualifying', 'semi_a', 'semi_b', 'final')
LABELS = {'qualifying': '예선', 'semi_a': '본선 A', 'semi_b': '본선 B', 'final': '결승'}


def duration(value: object) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return '-'
    if not math.isfinite(value) or value < 0:
        return '-'
    minutes, seconds = divmod(value, 60)
    return f'{int(minutes):02d}:{seconds:06.3f}'


def show_stage(root: Path, stage: str) -> bool:
    path = root / 'race' / 'results' / (stage + '.json')
    title = LABELS[stage]
    print(f'\n[{title}]')
    if not path.is_file():
        print('공식 기록 없음 (미실행 또는 저장 전)')
        return False
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f'결과 파일 읽기 오류: {exc}', file=sys.stderr)
        return False
    if not isinstance(payload, dict) or not isinstance(payload.get('results'), list):
        print('결과 파일 형식 오류', file=sys.stderr)
        return False

    state = payload.get('state', 'unknown')
    rows = payload['results']
    provisional = (bool(payload.get('provisional')) or
                   any(bool(r.get('rank_provisional')) for r in rows if isinstance(r, dict)))
    confirmed = (payload.get('valid') is True and state == 'complete' and not provisional)
    if confirmed:
        verdict = '확정 기록'
    elif payload.get('valid') is False and state == 'invalid':
        verdict = '무효 기록 (순위 사용 금지)'
    elif state == 'running':
        verdict = '진행 중 (완료된 팀만 표시, 최종 순위 아님)'
    elif provisional:
        verdict = '잠정 기록 (운영자 판정 필요)'
    else:
        verdict = '미확정 기록 (공식 순위로 사용 금지)'
    print(f'맵: {payload.get("track", "-")} | 목표: {payload.get("laps", "-")}랩 | {verdict}')
    if payload.get('error'):
        print(f'오류: {payload["error"]}')
    if not rows:
        print('기록된 참가팀 없음')
        return confirmed
    print('순위 | 팀       | 상태   | 완료 랩 | 총시간     | 비고')
    print('-' * 71)
    def order(row):
        rank = row.get('rank')
        return (rank if isinstance(rank, int) and not isinstance(rank, bool) else 999,
                str(row.get('entry_id', '')))
    for row in sorted((r for r in rows if isinstance(r, dict)), key=order):
        rank = row.get('rank')
        rank_s = str(rank) if isinstance(rank, int) and not isinstance(rank, bool) else '-'
        if row.get('rank_provisional'):
            rank_s += '*'
        team = str(row.get('entry_id', '-'))
        status = '완주' if row.get('status') == 'finished' else 'DNF'
        laps = str(row.get('laps', 0)) + '/' + str(payload.get('laps', '?'))
        elapsed = duration(row.get('time_seconds')) if status == '완주' else '-'
        reason = '판정 필요' if row.get('rank_provisional') else str(row.get('reason') or '-')
        print(f'{rank_s:>4} | {team:<8} | {status:<6} | {laps:>7} | {elapsed:>10} | {reason}')
    if provisional:
        print('* 동률·오차 등으로 판정이 필요한 잠정 순위입니다.')
    return confirmed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='URRC v24 공식 경기 순위 조회 (읽기 전용)')
    parser.add_argument('stage', nargs='?', choices=(*STAGES, 'all'), default='all')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    if not (root / 'race' / 'v24_profile.json').is_file():
        print('v24 공식 대회 폴더가 아닙니다.', file=sys.stderr)
        return 2
    try:
        profile = json.loads((root / 'race/v24_profile.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'v24 프로필 읽기 오류: {exc}', file=sys.stderr)
        return 2
    if profile.get('mode') != 'official':
        print('공식 대회 프로필에서만 결과를 조회할 수 있습니다.', file=sys.stderr)
        return 2
    stages = STAGES if args.stage == 'all' else (args.stage,)
    for stage in stages:
        show_stage(root, stage)
    print('\n실시간 진행 순위: bash race_v24.sh monitor <qualifying|semi_a|semi_b|final>')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
