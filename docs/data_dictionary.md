# CFPB model data dictionary

Generated from the saved configuration. Page references are one-based PDF page positions; printed User’s Guide pages are one lower. All 217 columns have a numerical profile in `outputs/tables/full_column_profile.csv`; unselected fields have not all received a semantic audit.

## Label

In a typical month, how difficult is it for you to cover your expenses and pay all your bills?

Codebook PDF 43; Guide PDF 82. Code 1 (not at all difficult) maps to 0; codes 2/3 (somewhat/very difficult) map to 1. Code -1 and standard missing labels are excluded, never imputed as negative.

## PPINCIMP

Original question or field source: Household income (panel-data variable; original panel question not reproduced in Appendix A)

Codebook PDF pages [79]; Guide PDF pages [66].

Valid codes: 1=Less than $20,000; 2=$20,000 to $29,999; 3=$30,000 to $39,999; 4=$40,000 to $49,999; 5=$50,000 to $59,999; 6=$60,000 to $74,999; 7=$75,000 to $99,999; 8=$100,000 to $149,999; 9=$150,000 or more

Special missing codes: No documented special codes; standard NA is still handled by training-set imputation.

Rationale: Household resources; categorical USD annual household income, not monthly individual AUD.

Proposed application prompt: Select your annual household income band in USD.

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## SAVINGSRANGES

Original question or field source: How much money do you have in savings today (in cash, checking, and savings account balances)?

Codebook PDF pages [45, 46]; Guide PDF pages [55, 84].

Valid codes: 1=$0; 2=$1-99; 3=$100-999; 4=$1,000-4,999; 5=$5,000-19,999; 6=$20,000-74,999; 7=$75,000 or more

Special missing codes: -1=Refused; 98=I do not know; 99=Prefer not to say

Rationale: Liquidity buffer; legitimate contemporary association, not a future predictor. Public-use bands differ from original survey.

Proposed application prompt: How much money do you have in savings today (in cash, checking, and savings account balances)?

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## EMPLOY

Original question or field source: Which one of the following would you say is your primary employment or work status?

Codebook PDF pages [75, 76]; Guide PDF pages [59, 60, 97].

Valid codes: 1=Self-employed; 2=Full-time employee or military; 3=Part-time employee or military; 4=Homemaker; 5=Full-time student; 6=Permanently sick, disabled or unable to work; 7=Unemployed or temporarily laid off; 8=Retired

Special missing codes: 99=Refused

Rationale: Income-source structure. Collapse codes 4–8 to one not-in-paid-employment category to avoid distinct disability/retirement indicators.

Proposed application prompt: Primary work status: self-employed, full-time, part-time, or not in paid employment; prefer not to say.

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Raw code 6 reveals health/disability and code 8 proxies age. Neither distinction retained by model; employment still a sensitive proxy. Fairness audit pending.

Transformation: {'1': '1', '2': '2', '3': '3', '4': '4', '5': '4', '6': '4', '7': '4', '8': '4'}. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## VOLATILITY

Original question or field source: Which of the following best describes how your household’s income changes from month to month, if at all?

Codebook PDF pages [48, 49]; Guide PDF pages [86].

Valid codes: 1=Roughly the same each month; 2=Roughly the same most months, with unusually high or low months; 3=Often varies quite a bit month to month

Special missing codes: -1=Refused

Rationale: Income predictability; not a bill-payment outcome.

Proposed application prompt: Which of the following best describes how your household’s income changes from month to month, if at all?

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## EARNERS

Original question or field source: How many people currently contribute to the income used to pay bills for your household?

Codebook PDF pages [48]; Guide PDF pages [86].

Valid codes: 1=One; 2=Two; 3=More than two

Special missing codes: -1=Refused

Rationale: Income support count; not household size and not exact count above two.

Proposed application prompt: How many people currently contribute to the income used to pay bills for your household?

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## HOUSING

Original question or field source: Which one of the following best describes your housing situation?

Codebook PDF pages [43]; Guide PDF pages [82].

Valid codes: 1=Own my home; 2=Rent; 3=Do not currently own or rent

Special missing codes: -1=Refused

Rationale: Housing context, not a mortgage payment amount.

Proposed application prompt: Which one of the following best describes your housing situation?

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## PRODHAVE_8

Original question or field source: Which of the following financial products and services do you currently have? Student/Education Loan (for yourself or someone else)

Codebook PDF pages [47]; Guide PDF pages [85].

Valid codes: 0=No; 1=Yes

Special missing codes: No documented special codes; standard NA is still handled by training-set imputation.

Rationale: Student-loan obligation indicator; no amount or delinquency inference. Unchecked survey checkbox coded 0, not verified absence of debt.

Proposed application prompt: Which of the following financial products and services do you currently have? Student/Education Loan (for yourself or someone else)

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.

## PPHHSIZE

Original question or field source: Household size (panel-data variable; original panel question not reproduced in Appendix A)

Codebook PDF pages [79]; Guide PDF pages [65, 66].

Valid codes: 1=1; 2=2; 3=3; 4=4; 5=5+

Special missing codes: No documented special codes; standard NA is still handled by training-set imputation.

Rationale: Resource-sharing context; top-coded five-plus, encoded categorically.

Proposed application prompt: How many people live in your household? 1, 2, 3, 4, 5+.

Availability: Self-reported contemporaneous input; not verified at credit application time

Sensitivity: Not an explicit protected attribute; income and housing may still proxy socioeconomic differences.

Transformation: Retain categories; never interpret range codes as money. Special missing values become NaN, followed by training-set mode imputation and OneHotEncoder.
