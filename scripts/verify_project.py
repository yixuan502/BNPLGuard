"""Verify a relocated project without training models or evaluating test data."""
from pathlib import Path
import csv
import hashlib
import importlib.metadata
import json
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import joblib
import numpy as np
import pandas as pd
from src.common import read_json, sha256, write_json


def verify():
    before = read_json('outputs/migration/2026-11-04/copy_integrity_before.json')
    old_root = before['original_root']
    expected_prefix = ROOT / '.venv'
    assert Path(sys.prefix) == expected_prefix, 'Wrong virtual environment'
    assert Path.cwd() == ROOT, 'Run from the active project root'
    changes = []
    for rel, evidence in before['copied_files'].items():
        p = ROOT / rel
        assert p.is_file(), f'Missing copied file: {rel}'
        if sha256(p) != evidence['sha256']:
            changes.append(rel)
    assert set(changes) == {'src/data_audit.py'}, changes
    # This source edit changes generated English prose only; preserve training evidence.
    pinned = {}
    for line in (ROOT / 'requirements.txt').read_text().splitlines():
        if '==' in line:
            package, wanted = line.split('==', 1)
            actual = importlib.metadata.version(package)
            assert actual == wanted, (package, wanted, actual)
            pinned[package] = actual
    launcher_paths = []
    for p in [ROOT / '.venv/pyvenv.cfg', *(ROOT / '.venv/bin').iterdir()]:
        if p.is_symlink():
            assert old_root not in str(p.resolve()), str(p)
        elif p.is_file():
            try:
                text = p.read_text()
            except UnicodeError:
                continue
            if old_root in text:
                launcher_paths.append(str(p.relative_to(ROOT)))
    assert not launcher_paths, launcher_paths
    cfg = read_json('config/model_config.json')
    data = pd.read_csv(ROOT / cfg['data_path']).set_index('PUF_ID', drop=False)
    split = read_json('data/splits/cfpb_split_ids.json')
    canonical = ROOT / 'models/cfpb/stage3_v2'
    manifest = json.loads((canonical / 'run_manifest.json').read_text())
    for name, digest in manifest['artifacts_sha256'].items():
        assert sha256(canonical / name) == digest, name
    assert sha256(ROOT / cfg['data_path']) == manifest['data_sha256']
    assert sha256(ROOT / 'data/splits/cfpb_split_ids.json') == manifest['split_sha256']
    saved = pd.read_csv(canonical / 'validation_predictions.csv')
    np.testing.assert_array_equal(saved.PUF_ID, split['validation'])
    model_checks = {}
    for name in ['dummy', 'logistic_regression']:
        pipeline = joblib.load(canonical / f'{name}.joblib')
        p = pipeline.predict_proba(data.loc[split['validation']])[:, 1]
        np.testing.assert_allclose(p, saved[name], rtol=0, atol=1e-14)
        model_checks[name] = {'validation_rows': len(p), 'max_absolute_difference_from_saved_csv': float(np.max(np.abs(p - saved[name])))}
    # Register Kaggle without source certification, target analysis or model fitting.
    candidates = sorted((ROOT / 'data').rglob('*BNPL*Dataset*.csv'))
    kaggle_files = []
    for p in candidates:
        with p.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.reader(stream)
            header = next(reader)
            row_count = sum(1 for _ in reader)
        kaggle_files.append({'path': str(p.relative_to(ROOT)), 'format': 'CSV', 'bytes': p.stat().st_size,
                             'rows': row_count, 'column_count': len(header), 'columns': header, 'sha256': sha256(p)})
    write_json('data/metadata/kaggle_inventory.json', {
        'checked_at': datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),
        'availability': 'present_and_readable' if kaggle_files else 'not_found', 'files': kaggle_files,
        'modeling_status': 'deferred', 'scope': 'File registration only; no training or cross-source merge.',
        'provenance_license_synthetic_status': 'Not yet audited. A local file does not establish authenticity.'})
    inventory = []
    for p in sorted([*(ROOT / 'data/raw').rglob('*'), *(ROOT / 'docs/references').glob('*.pdf')]):
        if p.is_file():
            inventory.append({'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha256(p),
                              'role': 'raw data' if p.suffix == '.csv' else 'reference material'})
    write_json('data/metadata/input_inventory.json', {
        'root': '.', 'path_policy': 'All active file entries are relative to the project root.',
        'checked_on': '2026-11-04', 'files': inventory,
        'kaggle_raw_found': bool(kaggle_files), 'kaggle_status': 'deferred',
        'historical_inventory': 'outputs/migration/2026-11-04/authored_files_before_translation.zip',
        'optional_reference_notebook_present': bool(list((ROOT/'data').rglob('*.ipynb'))),
        'note': 'Original input names and locations are preserved in the archive. Do not treat historical paths as active inputs.'})
    authored = [ROOT/'README.md', ROOT/'AGENTS.md']
    for folder in ['src', 'tests', 'scripts', 'config', 'docs', 'models', 'data/metadata']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix in {'.md', '.py', '.json', '.txt'} and 'references' not in p.parts and '__pycache__' not in p.parts:
                authored.append(p)
    chinese = []
    old_paths = []
    for p in authored:
        text = p.read_text()
        if re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]', text):
            chinese.append(str(p.relative_to(ROOT)))
        if old_root in text:
            old_paths.append(str(p.relative_to(ROOT)))
    assert not chinese, chinese
    assert not old_paths, old_paths
    report = {
        'checked_at': datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),
        'project_root': str(ROOT), 'python_executable': sys.executable, 'sys_prefix': sys.prefix,
        'copy_files_compared_before_edits': len(before['copied_files']),
        'copy_missing_before_edits': before['missing'], 'copy_differences_before_edits': before['different'],
        'source_changes_after_copy': changes, 'source_change_purpose': 'English generated dictionary prose only',
        'pinned_dependencies': pinned, 'raw_data_configs_splits_models_preserved': True,
        'canonical_artifact_hashes_match_original_manifest': True, 'models_loaded_without_retraining': model_checks,
        'active_old_absolute_paths': old_paths, 'old_paths_in_new_environment_launchers': launcher_paths,
        'authored_text_files_scanned': len(authored), 'authored_files_with_Chinese_text': chinese,
        'kaggle_files_registered': kaggle_files, 'test_evaluated': False,
        'excluded_historical_material': ['.venv.pre_migration/', 'outputs/migration/2026-11-04/authored_files_before_translation.zip', 'outputs/migration/2026-11-04/copy_integrity_before.json'],
        'pytest_log': (ROOT/'outputs/migration/2026-11-04/pytest.txt').read_text().strip(),
        'audit_log': (ROOT/'outputs/migration/2026-11-04/data_audit.txt').read_text().strip(),
        'pip_check_log': (ROOT/'outputs/migration/2026-11-04/pip_check.txt').read_text().strip(),
    }
    write_json('outputs/migration/2026-11-04/verification.json', report)
    print('PASS: desktop environment, pinned packages, preserved artifacts, validation inference, English text and active paths.')
    print(f'Kaggle files: {len(kaggle_files)}. Test set remains unevaluated.')
    return report

if __name__ == '__main__':
    verify()
