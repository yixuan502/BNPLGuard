# User-testing feedback: receipt and verification

Reviewed 5 November 2026. This is an evidence-processing note, not the course report.

## Source and verification

The user supplied a compiled workbook with Sessions, Responses, Summary and S1 Interpretations sheets. A byte-identical copy is retained separately outside the source project and excluded from publication. SHA256: `e58fbd8bd7d914c7003198a581d17cf8b0b8cc8ee688194822ee62d69d70337f`. No original workbook cells, cached formula values, metadata or scores were changed.

The workbook records three consenting nondevelopers and app commit `771aadd`; these are source-recorded statements, not independent attendance/version verification. Session dates are absent. Original participant forms, screenshots and recordings were not supplied with this workbook in this review. Some English wording is normalized or translated; it must not be presented as independently verified verbatim testimony.

`scripts/review_user_feedback.py` reads OOXML without executing macros/external links. It recomputes both fictional case answer keys through the existing simulator, checks all 36 simulator responses against the prespecified scoring rule, reconciles per-participant and overall totals, and checks the two Summary formulas and their cached values. Workbook recalculation or visual redesign was neither necessary nor performed. Aggregate evidence is saved in `outputs/user_testing/feedback_review_v1/review.json`; it omits individual comments, devices, authors and local user paths.

## Recorded findings

| Measure | Result | Interpretation |
|---|---:|---|
| Independent text responses | 16/18 (88.9%); participant totals 6, 6, 4 out of 6 | All text items are recorded as H0 |
| All recorded app responses | 18/18 (100%) | Mix of independent and assisted answers |
| Explicitly unassisted app responses | 6/6, one participant | Not evidence that all three succeeded independently |
| App responses after H2/H3 operational guidance | 12/12, two participants | Original pre-guidance app responses are missing; do not infer zeros or carry assisted answers into independent scores |
| Screen interpretation | Workbook records 2/2 for each participant | Cannot independently rescore: source says original wording is partly obscured; only English summaries are provided |
| Subjective clarity | Mean/median 4/5; range 3–5; n=3 | Subjective ordinal rating, separate from objective understanding |
| Median active time | Text 142 seconds; app 155 seconds | Different cases and mixed assistance; not evidence of a speed improvement |

The two incorrect text responses concern Case A: combined final buffer was recorded as -200 instead of -100 AUD, and change from current as -1100 instead of -1000 AUD. All recorded answer keys and 36 item scores agree with the unchanged simulator. The totals are item-level descriptions; the 18 answers are not 18 independent participants.

Translated feedback describes scenario comparison as clear, raises initial confusion between emergency savings and monthly income, and notes that app field order differed from the task sheet. These are candidate usability improvements, not implemented fixes. No application behavior was changed in response.

## Limits and remaining checks

The data support a narrow descriptive statement: recorded final app answers were correct, including answers after operational guidance, in this three-person workbook. They do not establish a causal improvement, independent success for all users, financial behavior change, market adoption, or general population usability. Text always came first; cases differ; case allocation is 2:1; practice, assistance and the high text baseline constrain interpretation.

Before stronger reporting, obtain original pre-H2/H3 app answers (if they were actually collected), legible original S1 wording, and session dates. Clarify the nonzero assisted duration in the session marked H0: duration alone does not prove substantive assistance. Retain H2/H3 operation codes even where narrative notes say navigation; do not relabel them H1 without source confirmation. Do not retrospectively invent missing records. Confirm translated feedback against original wording before quoting it.

Blank structured instruments are included in `user_testing/materials_v1`; they are distinct from the collected participant records.

## Reproduce the audit locally

From the project root, with the privately held source workbook:

```bash
.venv/bin/python scripts/review_user_feedback.py --input /path/to/private/submitted_feedback.xlsx --output-dir outputs/user_testing/feedback_review_v2
```

Use a new output directory to preserve prior receipts. No training, formal model evaluation, deployment or external API is performed by this audit.
