"""Read a submitted study workbook without changing it; export aggregate evidence only.

Run from the project root with --input PATH --output-dir PATH.
Original workbooks and identifiable metadata must remain outside Git.
"""
import argparse
from collections import Counter
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import statistics
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / 'src').exists():
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from src.simulator_presentation import run_simulation

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def load_cells(path):
    """Read OOXML values/formulas directly. Do not execute workbook code or links."""
    with ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(s.itertext()) for s in ET.fromstring(
                archive.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        relations = {r.get('Id'): r.get('Target') for r in ET.fromstring(
            archive.read('xl/_rels/workbook.xml.rels'))}
        sheets, formulas = {}, {}
        for sheet in ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
            name = sheet.get('name')
            target = relations[sheet.get('{'+NS['r']+'}id')]
            member = target.lstrip('/') if target.startswith('/') else 'xl/'+target
            cells = {}
            for c in ET.fromstring(archive.read(member)).findall('.//m:sheetData/m:row/m:c', NS):
                value, inline, formula = c.find('m:v', NS), c.find('m:is', NS), c.find('m:f', NS)
                text = value.text if value is not None else ''.join(inline.itertext()) if inline is not None else None
                if c.get('t') == 's' and text is not None:
                    text = shared[int(text)]
                if c.get('t') == 'e':
                    raise ValueError(f'Workbook error: {name}!{c.get("r")}')
                if text is not None:
                    cells[c.get('r')] = text
                if formula is not None:
                    formulas[f'{name}!{c.get("r")}'] = {'formula': formula.text, 'cached': text}
            sheets[name] = cells
    return sheets, formulas


def rows(cells, columns):
    last = max(int(''.join(filter(str.isdigit, a))) for a in cells)
    return [{col: cells.get(f'{col}{r}') for col in columns}
            for r in range(2, last+1) if cells.get(f'A{r}')]


def review(path):
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    sheets, formulas = load_cells(path)
    assert set(sheets) == {'Sessions', 'Responses', 'Summary', 'S1 Interpretations'}
    sessions = rows(sheets['Sessions'], 'ABCDEFGHIJKLMNOPQ')
    responses = rows(sheets['Responses'], 'ABCDEFGHIJ')
    assert len(sessions) == 3 and len(responses) == 39
    ids = [s['A'] for s in sessions]
    assert len(set(ids)) == 3
    assert Counter(r['A'] for r in responses) == Counter({p: 13 for p in ids})
    assert len({(r['A'], r['B'], r['D']) for r in responses}) == 39
    fixtures = json.loads((ROOT/'user_testing/materials_v1/cases_verified.json').read_text())
    keys = {}
    for case, fixture in fixtures.items():
        result = run_simulation(fixture['inputs'], income_drop=0.2, bnpl_reduction=0)
        scenario = {r['key']: r for r in result['scenarios']}
        current = scenario['current']['metrics']['cash_buffer']['value']
        added = scenario['added_bnpl']
        both = scenario['added_bnpl_income_shock']
        keys[case] = [current, added['metrics']['cash_buffer']['value'],
                      added['delta_from_current']['cash_buffer']['value'],
                      both['metrics']['cash_buffer']['value'],
                      both['delta_from_current']['cash_buffer']['value'], 'Shortfall']
    verified = []
    for r in responses:
        if r['B'] == 'Screen':
            continue
        expected = keys[r['C']][int(r['D'][1:])-1]
        numeric = r['D'][-1] != '6'
        agrees = (Decimal(r['F']) == Decimal(expected)) if numeric else r['F'].strip().lower() == expected.lower()
        assert (Decimal(r['G']) == Decimal(expected)) if numeric else r['G'].lower() == expected.lower()
        assert int(r['H']) == int(agrees), (r['A'], r['D'], 'Recorded score disagrees with answer')
        verified.append((r, int(agrees)))
    totals = {phase: sum(score for r, score in verified if r['B'] == phase) for phase in ['Text', 'App']}
    assert totals == {'Text': 16, 'App': 18}
    summary = sheets['Summary']
    for s in sessions:
        pid = s['A']
        assert {r['C'] for r in responses if r['A'] == pid and r['B'] == 'Text'} == {s['B']}
        assert {r['C'] for r in responses if r['A'] == pid and r['B'] == 'App'} == {s['C']}
        sr = next(int(a[1:]) for a, v in summary.items() if a.startswith('A') and v == pid)
        assert int(summary[f'B{sr}']) == sum(score for r, score in verified if r['A'] == pid and r['B'] == 'Text')
        assert int(summary[f'C{sr}']) == sum(score for r, score in verified if r['A'] == pid and r['B'] == 'App')
    assert Decimal(summary['B8']) == totals['Text'] and Decimal(summary['B10']) == totals['App']
    assert Decimal(summary['B9']) == 18 and Decimal(summary['B11']) == 18
    assert abs(Decimal(formulas['Summary!E7']['cached']) - Decimal(16)/18) < Decimal('1e-14')
    assert Decimal(formulas['Summary!E8']['cached']) == 1
    clarity = [int(s['N']) for s in sessions]
    assert Decimal(summary['B12']) == Decimal(sum(clarity))/3
    app_unassisted = [(r, score) for r, score in verified if r['B'] == 'App' and r['I'] == 'H0']
    app_assisted = [(r, score) for r, score in verified if r['B'] == 'App' and r['I'] != 'H0']
    assert len(app_unassisted) == 6 and len(app_assisted) == 12
    result = {
        'reviewed_on': datetime.now(ZoneInfo('Australia/Sydney')).date().isoformat(),
        'source_sha256': before,
        'source_type': 'User-supplied compiled workbook; original session sheets/screenshots not supplied in this review',
        'participants_reported': 3,
        'consent_yes_recorded': sum(s['H'] == 'Yes' for s in sessions),
        'nondeveloper_yes_recorded': sum(s['G'] == 'Yes' for s in sessions),
        'app_commits_recorded': sorted({s['F'] for s in sessions}),
        'test_dates_recorded': False,
        'simulator_items_rescored': 36,
        'answer_key_and_recorded_scores': 'All 36 numeric/status scores agree with the existing simulator',
        'summary_formula_review': 'Two formulas and their cached values agree; static totals independently recomputed; workbook not edited/recalculated',
        'text': {'correct': 16, 'items': 18, 'percent': 100*16/18, 'phase_totals_out_of_6': sorted(int(summary[f'B{r}']) for r in [2,3,4])},
        'app_recorded': {'correct': 18, 'items': 18, 'percent': 100., 'qualification': 'Mix of independent and post-guidance responses'},
        'app_unassisted_recorded': {'correct': sum(s for _,s in app_unassisted), 'items': 6, 'participants': 1},
        'app_after_operational_guidance': {'correct': sum(s for _,s in app_assisted), 'items': 12, 'participants': 2},
        'missing_independent_app_item_responses': 12,
        'screen': {'recorded_total': 6, 'possible_total': 6, 'independently_rescored': False, 'reason': 'Only English summaries; workbook says originals are partially obscured in screenshots unavailable here'},
        'subjective_clarity': {'scale': '1-5', 'n': 3, 'mean': statistics.mean(clarity), 'median': statistics.median(clarity), 'range': [min(clarity), max(clarity)]},
        'timing_seconds': {phase: {'n': 3, 'mean': statistics.mean(float(s[c]) for s in sessions), 'median': statistics.median(float(s[c]) for s in sessions)} for phase,c in [('text','I'),('app','J')]},
        'feedback_themes': ['Scenario comparison was described as clear', 'Savings stock was initially confused with monthly income', 'Input ordering differed from the task sheet'],
        'feedback_wording': 'Workbook contains translated/English-normalized comments, not independently verified verbatim quotes',
        'pending_clarifications': [
            'Obtain original independent app answers before H2/H3; do not replace missing originals with assisted scores',
            'Obtain legible original S1 answers/screenshots and confirm their scoring',
            'Confirm test dates and version attribution; commit is recorded by the workbook, not independently logged',
            'Clarify nonzero assisted seconds for a session marked H0; do not infer it received substantive help',
            'H2/H3 operational prompts should remain differentiated from navigation-only H1 wording',
        ],
        'scope': 'Descriptive convenience sample; text-first order, different cases, practice, assistance and ceiling effects prevent a causal effectiveness claim',
        'publication': 'Aggregate review only; original workbook, author/path metadata, device details and individual feedback remain private',
    }
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = review(args.input)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir/'review.json'
    if output.exists():
        raise FileExistsError('Preserve an existing review; choose a new output directory')
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'source_unchanged': True, 'items_rescored': 36,
                      'text': '16/18', 'app_recorded': '18/18; 12 assisted items',
                      'output': str(output)}, indent=2))


if __name__ == '__main__':
    main()
