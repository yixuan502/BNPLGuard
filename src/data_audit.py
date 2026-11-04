"""Local-only CFPB audit; never downloads or modifies original files."""
import pandas as pd
import numpy as np
from .common import ROOT, read_json, write_json, sha256
from .preprocessing import map_target, clean_features

def audit():
    cfg = read_json('config/model_config.json')
    path = ROOT / cfg['data_path']
    if not path.exists():
        raise FileNotFoundError(f'Place the existing CFPB CSV here: {path}; do not redownload it.')
    df = pd.read_csv(path)
    manifest = read_json('data/metadata/source_manifest.json')
    if sha256(path) != manifest['local_csv_sha256']:
        raise ValueError('Raw checksum changed. Review provenance and create a new version before training.')
    schema = read_json('config/feature_schema.json')['features']
    y = map_target(df.ENDSMEET)
    x = clean_features(df)
    expected = read_json('data/metadata/codebook_expected_counts.json')
    checks = {}
    for col, counts in expected.items():
        actual = {str(k): int(v) for k, v in df[col].value_counts().sort_index().items()}
        checks[col] = {'match': actual == counts, 'actual': actual, 'codebook': counts}
    profile = []
    for name in df:
        s = df[name]
        profile.append({'field':name,'dtype':str(s.dtype),'n':len(s),'standard_missing':int(s.isna().sum()),'unique':int(s.nunique()),'negative_codes_count':int((s < 0).sum()) if pd.api.types.is_numeric_dtype(s) else None,'min':s.min(),'max':s.max(),'codebook_enum_verified':name in checks})
    pd.DataFrame(profile).to_csv(ROOT/'outputs/tables/full_column_profile.csv',index=False)
    write_json('outputs/tables/raw_value_counts.json', {c:{str(k):int(v) for k,v in df[c].value_counts(dropna=False).items()} for c in df if c not in ['PUF_ID','finalwt']})
    missing = [{'field':c,'n':len(df),'standard_missing':int(df[c].isna().sum()),'special_missing':int(df[c].isin([int(k) for k in m['missing_codes']]).sum()),'combined_missing':int(x[c].isna().sum()),'combined_missing_rate':float(x[c].isna().mean())} for c,m in schema.items()]
    pd.DataFrame(missing).to_csv(ROOT/'outputs/tables/feature_missingness.csv',index=False)
    included = y.notna()
    flows = [{'step':'raw','n':len(df)},{'step':'exclude missing label','n':int((~included).sum())},{'step':'eligible','n':int(included.sum())},{'step':'negative label','n':int((y==0).sum())},{'step':'positive label','n':int((y==1).sum())}]
    pd.DataFrame(flows).to_csv(ROOT/'outputs/tables/sample_flow.csv',index=False)
    failures=[]
    if df.PUF_ID.isna().any() or df.PUF_ID.duplicated().any(): failures.append('Missing or repeated respondent ID')
    if df.duplicated().any(): failures.append('Duplicate records')
    if not all(c['match'] for c in checks.values()): failures.append('Model fields differ from local Codebook frequencies')
    if not np.isfinite(df.finalwt).all() or not (df.finalwt>0).all(): failures.append('Invalid weights')
    result={'rows':len(df),'columns':len(df.columns),'duplicate_records':int(df.duplicated().sum()),'duplicate_ids':int(df.PUF_ID.duplicated().sum()),'standard_missing_total':int(df.isna().sum().sum()),'eligible':int(included.sum()),'positive':int((y==1).sum()),'negative':int((y==0).sum()),'positive_rate':float(y[included].mean()),'excluded_label':int((~included).sum()),'model_field_codebook_checks':checks,'sampling_groups':{str(k):int(v) for k,v in df['sample'].value_counts().items()},'weight_min':float(df.finalwt.min()),'weight_max':float(df.finalwt.max()),'weighted_eligible_prevalence_descriptive':float(np.average(y[included],weights=df.loc[included,'finalwt'])),'gate_passed':not failures,'failures':failures,'full_file_scope':'All 217 columns profiled; exact semantic/enum/frequency verification for label and eight model fields. Other fields excluded from modeling, not certified.'}
    write_json('outputs/metrics/data_audit.json',result)
    dictionary = [
        '# CFPB model data dictionary\n',
        'Generated from the saved configuration. Page references are one-based PDF page positions; printed User’s Guide pages are one lower. All 217 columns have a numerical profile in `outputs/tables/full_column_profile.csv`; unselected fields have not all received a semantic audit.\n',
        '## Label\n', read_json('config/label_mapping.json')['question'] + '\n',
        'Codebook PDF 43; Guide PDF 82. Code 1 (not at all difficult) maps to 0; codes 2/3 (somewhat/very difficult) map to 1. Code -1 and standard missing labels are excluded, never imputed as negative.\n',
    ]
    for name, m in schema.items():
        dictionary += [
            f'## {name}\n',
            f"Original question or field source: {m['question']}\n",
            f"Codebook PDF pages {m['codebook_pdf_pages']}; Guide PDF pages {m['guide_pdf_pages']}.\n",
            'Valid codes: ' + json_codes(m['labels']) + '\n',
            'Special missing codes: ' + (json_codes(m['missing_codes']) or 'No documented special codes; standard NA is still handled by training-set imputation.') + '\n',
            f"Rationale: {m['reason']}\n",
            f"Proposed application prompt: {m['app_prompt']}\n",
            f"Availability: {m['available_at_screening']}\n",
            f"Sensitivity: {m.get('sensitivity_note', 'Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.')}\n",
            f"Transformation: {m.get('transform', 'Retain categories; never interpret range codes as money')}. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.\n",
        ]
    (ROOT/'docs/data_dictionary.md').write_text('\n'.join(dictionary))
    print(f"Gate={'PASS' if not failures else 'FAIL'}: {len(df)} x {len(df.columns)}, eligible={included.sum()}, positives={(y==1).sum()} ({y[included].mean():.4%})")
    if failures: raise ValueError('; '.join(failures))
    return result

def json_codes(mapping):
    return '; '.join(f'{k}={v}' for k,v in mapping.items())

if __name__ == '__main__':
    audit()
