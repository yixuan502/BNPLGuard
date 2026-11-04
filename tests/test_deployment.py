"""Portable release checks: files, frozen objects, compatibility and isolated packaging."""
import json,tomllib
from src.common import ROOT,read_json
from src.deployment import audit,build,release_files


def test_reviewed_release_paths_and_frozen_hashes():
    receipt=audit();files=release_files()
    assert receipt['file_count']>50
    assert 'models/cfpb/stage4_v1/logistic_regression.joblib' in files
    assert 'models/cfpb/explanations_v1/background_encoded.npz' in files
    assert 'data/splits/cfpb_split_ids.json' in files
    assert not any('/raw/' in x or 'test_predictions' in x or x.endswith('.pdf') for x in files)


def test_cloud_python_and_model_dependency_versions_are_explicit():
    project=tomllib.loads((ROOT/'pyproject.toml').read_text());lock=tomllib.loads((ROOT/'uv.lock').read_text())
    assert project['project']['requires-python']=='>=3.13,<3.14'
    pins={p['name']:p['version'] for p in lock['package'] if 'version' in p}
    assert pins['scikit-learn']=='1.9.1' and pins['numpy']=='2.5.4' and pins['shap']=='0.54.1'
    assert pins['streamlit']=='1.66.1' and pins['pandas']=='3.1.0'


def test_clean_tree_contains_exactly_the_reviewed_files(tmp_path):
    out=tmp_path/'release';receipt=build(out)
    assert {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}==set(release_files())
    assert audit(out)['files_sha256']==receipt['files_sha256']
    assert not (out/'data/raw').exists() and not (out/'.venv').exists()
