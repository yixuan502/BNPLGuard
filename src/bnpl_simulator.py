"""Pure monthly cash-flow calculations; no datasets, models or file operations."""
from dataclasses import dataclass, replace
from fractions import Fraction
from .input_validation import FinancialInputs, ScenarioSettings


@dataclass(frozen=True)
class Metric:
    value: Fraction | None
    unit: str
    reason: str | None = None


@dataclass(frozen=True)
class MonthlyMetrics:
    total_bnpl: Metric
    total_repayments: Metric
    monthly_outflows: Metric
    cash_buffer: Metric
    repayment_to_income: Metric
    savings_coverage: Metric


@dataclass(frozen=True)
class ScenarioResult:
    key: str
    title: str
    effective_inputs: FinancialInputs
    metrics: MonthlyMetrics
    deltas: MonthlyMetrics
    assumptions: tuple[str, ...]


COMMON_ASSUMPTIONS = (
    'All amounts use one currency and a monthly time unit; no foreign-exchange conversion is performed.',
    'Income is monthly after-tax income. E excludes every repayment already counted in D, B0 or Bnew.',
    'D contains non-BNPL repayments only; B0 and Bnew contain BNPL repayments only.',
    'Emergency savings coverage assumes no new income and unchanged expenses and repayments; it is not actual time until funds run out.',
    'A positive monthly buffer does not guarantee enough cash on each payment due date.',
    'These are deterministic scenario calculations, not empirical model results or BNPL default probabilities.',
)


def calculate_monthly(inputs):
    if not isinstance(inputs, FinancialInputs):
        raise TypeError('Use validated FinancialInputs')
    b = inputs.B0 + inputs.Bnew
    repayments = inputs.D + b
    outflows = inputs.E + repayments
    return MonthlyMetrics(
        total_bnpl=Metric(b, inputs.currency),
        total_repayments=Metric(repayments, inputs.currency),
        monthly_outflows=Metric(outflows, inputs.currency),
        cash_buffer=Metric(inputs.I - outflows, inputs.currency),
        repayment_to_income=Metric(repayments / inputs.I, 'ratio') if inputs.I else Metric(None, 'ratio', 'Monthly income is zero; repayment-to-income ratio is undefined.'),
        savings_coverage=Metric(inputs.S / outflows, 'months') if outflows else Metric(None, 'months', 'Monthly expenses and repayments total zero; savings coverage has no defined denominator.'),
    )


def metric_deltas(metrics, baseline):
    values = {}
    for name in MonthlyMetrics.__dataclass_fields__:
        current = getattr(metrics, name); original = getattr(baseline, name)
        if current.value is None or original.value is None:
            reason = 'Change is unavailable because '
            reason += ('the current-case metric is unavailable: ' + original.reason) if original.value is None else ('this scenario metric is unavailable: ' + current.reason)
            values[name] = Metric(None, current.unit, reason)
        else:
            values[name] = Metric(current.value - original.value, current.unit)
    return MonthlyMetrics(**values)


def compare_scenarios(inputs, settings):
    """Every independent scenario derives from current, never from another result."""
    if not isinstance(inputs, FinancialInputs) or not isinstance(settings, ScenarioSettings):
        raise TypeError('Use validated inputs and settings')
    if settings.bnpl_reduction > inputs.B0:
        raise ValueError('BNPL reduction exceeds B0')
    current = replace(inputs, Bnew=Fraction(0))
    shocked_income = inputs.I * (1 - settings.income_drop)
    specifications = (
        ('current', 'Current', current,
         ('Proposed Bnew is excluded; all other submitted amounts are retained.',)),
        ('added_bnpl', 'Added BNPL', replace(current, Bnew=inputs.Bnew),
         ('Apply proposed Bnew to current; income and all other amounts are unchanged.',)),
        ('income_shock', 'Income shock', replace(current, I=shocked_income),
         ('Apply income_drop to original income I; proposed Bnew remains excluded.',)),
        ('added_bnpl_income_shock', 'Added BNPL + income shock', replace(current, I=shocked_income, Bnew=inputs.Bnew),
         ('Apply both proposed Bnew and income_drop to current in this explicitly combined scenario.',)),
        ('reduced_existing_bnpl', 'Reduced existing BNPL', replace(current, B0=inputs.B0-settings.bnpl_reduction),
         ('Subtract the user-selected reduction from B0; income is unchanged and proposed Bnew is excluded.',
          'This is a user-defined hypothetical assumption, not permission to reduce or change contractual repayments.')),
    )
    baseline = calculate_monthly(current)
    return tuple(ScenarioResult(key, title, effective, calculate_monthly(effective),
                 metric_deltas(calculate_monthly(effective), baseline),
                 COMMON_ASSUMPTIONS + assumptions)
                 for key, title, effective, assumptions in specifications)
