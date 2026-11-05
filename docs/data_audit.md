# CFPB data audit and feasibility gate

Audit date: 4 November 2026. Code: `src/data_audit.py`. Machine-readable evidence: `outputs/metrics/data_audit.json`.

## Files and provenance

The active desktop project is `/Users/oneone/Desktop/BNPLGuard`. The initial analysis was performed in a separate workspace and subsequently copied here by the user. Current runtime data paths are project-relative; the current inventory is in `data/metadata/input_inventory.json`.

| Initial input | Format and role | Current treatment |
|---|---|---|
| NFWBS_PUF_2016_data (1).csv | Original CFPB CSV, 2,992,071 bytes | Identical frozen project copy at data/raw/cfpb/NFWBS_PUF_2016_data.csv |
| cfpb_nfwbs-puf-codebook.pdf | 91-page September 2017 Codebook | Existing copy in docs/references; no duplicate download |
| bnpl-credit-risk-insights.ipynb | Notebook v4, 18 cells, 4,969,107 bytes in the initial inventory | Reference only, never executed; check the current inventory for availability after copying |
| project-a-tech-team.pdf | Five-page course assignment | Entire document was extracted and read; retained in docs/references |
| marking-criteria-a-tech-team.pdf | Seven-page marking criteria | Entire document was extracted and read; retained in docs/references |
| FINS5557_BNPLGuard_Codex_Prompt_v2.md | User's original project specification | English maintained version in docs/project_spec.md; original wording retained in migration backup |

The original inspection found no Kaggle raw CSV or archive. The user subsequently announced a CSV upload; availability is verified independently in `data/metadata/kaggle_inventory.json`. A Notebook path such as `/kaggle/input/...` is not a local Mac file and does not establish data provenance or shape.

The [official landing page](https://www.consumerfinance.gov/data-research/financial-well-being-survey-data/) was checked during stage 3: survey year 2016, public-use release September 2017. The only missing official document downloaded was the [User’s Guide](https://www.consumerfinance.gov/documents/5588/cfpb_nfwbs-puf-user-guide.pdf), 98 pages, including the full survey instrument in Appendix A. Its date matches the local Codebook. The current [Codebook URL](https://www.consumerfinance.gov/documents/5586/cfpb_nfwbs-puf-codebook.pdf) timed out in online preview; the user's existing document was inspected instead.

Frozen CSV SHA256: `3680d33576549a99a8dfd7f99d5661a36a8fc1aac0d66f2bf2ec5524695304d8`.

The official CSV received an HTTP HEAD request only; headers are retained in `data/metadata/cfpb_csv_http_headers.txt`. No second raw dataset was downloaded. No official SHA256 was available. Version correspondence is supported by the release and filename, dimensions, local Codebook and exact frequencies of every model input and the label. The user's original download date is unknown; filesystem timestamps are not download evidence. The public-use file is intended for research and omits respondent PII, but no separate dataset license was identified in the reviewed material. Raw data and course PDFs are not automatically redistributed.

## Quality and grain

- 6,394 rows, 217 columns. Every column has a type, standard missing count, negative-code count, range and distinct-value profile. Full categorical frequencies are also saved.
- No duplicate rows, no duplicate PUF_ID, and no standard NA values. Special response codes are not counted as ordinary NA until explicitly mapped.
- One respondent per row. Guide PDF page 11 states that only one panelist per household was selected. No repeated-person or repeated-household structure was identified. There is no future outcome/time design.
- sample=1 contains 5,000 respondents, sample=2 contains 999, and sample=3 contains 395. The latter samples reflect older-adult and race/poverty oversampling rather than repeated observations.
- finalwt is the full-sample survey weight; values are finite and positive. See the audit JSON for its exact range. Guide PDF pages 35–36 require weights for population analysis. The baseline is explicitly an unweighted sample model with weighted validation sensitivity, not a population confidence interval or complete complex-survey inference.
- The target and all eight model inputs have exact Codebook code/frequency matches. All 217 fields were profiled, but full semantic certification of every unused field is not claimed.

## Missing and special values

SAVINGSRANGES -1/98/99 occur in 1,184 records (18.5174%); EMPLOY=99 in 116; VOLATILITY=-1 in 64; EARNERS=-1 in 78; HOUSING=-1 in 42. These specific values become NaN inside the model Pipeline. Income, household size and education-loan ownership currently have no such missing values.

Do not apply a blanket negative-value or 99 replacement to the entire dataset. Guide PDF page 42 distinguishes unknown county (-5), database recording errors (-4), cleaned/invalid answers (-3), skipped questions (-2), unanswered items (-1), and field-specific 8/98/99 responses. CONNECT can legitimately take 98 or 99. Unused fields remain unchanged. A multi-select zero means the item was not selected, not independently confirmed absence of that product.

## Label and sample flow

Question: In a typical month, how difficult is it for you to cover your expenses and pay all your bills?

| Original value | Meaning | Count | Main label |
|---|---|---:|---|
| 1 | Not at all difficult | 3,896 | 0 |
| 2 | Somewhat difficult | 1,975 | 1 |
| 3 | Very difficult | 479 | 1 |
| -1 | Refused/unanswered | 44 | Excluded |

6,394 records minus 44 missing labels leaves 6,350 eligible respondents: 3,896 negative and 2,454 positive (38.6457%). No rows are removed for feature missingness. The main mapping was fixed before model results. A severe-only definition, 3 versus 1/2, is a potential separate sensitivity study and has not been run. The target is contemporaneous difficulty, not observed bill default.

## Feasibility decision and unresolved issue

The Data Feasibility Gate passes for the selected label and feature set: a genuine question, adequate classes, clear codes, unique IDs and no obvious target-restatement inputs. See `data_dictionary.md` and `leakage_review.md`. This supports the sample baseline, not blanket certification of every source field.

Unused PCTLT200FPL differs from Codebook PDF page 81. The Codebook reports -5:395, 0:4501, 1:1498; the CSV reports -5:395, 0:4548, 1:1451. The difference is 47 records between categories 0 and 1. Its cause is unresolved; the 40% boundary language in Guide PDF page 68 also needs care. Values are preserved and the field is excluded. Resolve version/coding evidence before any future use; do not edit observations to match a published table.

HTTP HEAD returned 200 and Content-Length 2,992,071, matching the local length. Last-Modified was 17 March 2026; this is a server timestamp, not a new survey year. The remote ETag differs from the local MD5, but its checksum semantics are not documented. Byte identity with the current server therefore remains unverified. The operational version is the local SHA256-frozen file.
