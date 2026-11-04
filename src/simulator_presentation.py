"""Serializable web-facing responses and reviewed English rule templates."""
from dataclasses import asdict
from decimal import Decimal, localcontext, MAX_EMAX, MIN_EMIN
from fractions import Fraction
from .input_validation import AMOUNT_FIELDS, SimulationInputError, validate_inputs
from .bnpl_simulator import compare_scenarios, MonthlyMetrics

NOTICE = 'Illustrative scenario—not empirical model results'
LIMITATIONS = (
    'Monthly simplified model: no dated payment calendar, instalment schedule, fees, interest accrual or changes in contract balances are modeled.',
    'Savings S is held fixed across scenarios; the model does not simulate repeated monthly depletion.',
    'Income shocks and BNPL reductions are user assumptions, not forecasts or regulatory thresholds.',
    'No model score, survey code, credit decision, safe borrowing limit or default probability is calculated.',
)


def decimal_text(value):
    """JSON-safe decimal text; exact rational arithmetic precedes 28-digit serialization."""
    with localcontext() as context:
        context.prec = 28; context.Emax = MAX_EMAX; context.Emin = MIN_EMIN
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def inputs_dict(inputs):
    return {**{name: decimal_text(getattr(inputs, name)) for name in AMOUNT_FIELDS}, 'currency': inputs.currency}


def metric_dict(metric):
    return {'status': 'unavailable' if metric.value is None else 'ok',
            'value': None if metric.value is None else decimal_text(metric.value),
            'unit': metric.unit, 'reason': metric.reason}


def display_metric(metric, *, change=False):
    if metric.value is None:
        return {'text': 'N/A', 'reason': metric.reason}
    with localcontext() as context:
        context.prec = 40; context.Emax = MAX_EMAX; context.Emin = MIN_EMIN
        value = Decimal(decimal_text(metric.value))
        if metric.unit == 'ratio':
            text = f'{value * 100:,.2f} percentage points' if change else f'{value * 100:,.2f}%'
        elif metric.unit == 'months':
            text = f'{value:,.3f} months'
        else:
            text = f'{metric.unit} {value:,.2f}'
    return {'text': text, 'reason': None}


def rule_notices(scenario):
    """Messages describe arithmetic outcomes without invented risk cutoffs."""
    messages = []
    if scenario.metrics.cash_buffer.value < 0:
        messages.append({'code': 'negative_cash_flow', 'message': 'Under these assumptions, monthly expenses and repayments exceed income.'})
    elif scenario.metrics.cash_buffer.value == 0:
        messages.append({'code': 'zero_cash_buffer', 'message': 'Income exactly matches the listed monthly outflows; no monthly cash buffer remains.'})
    if scenario.effective_inputs.I == 0:
        messages.append({'code': 'zero_income', 'message': 'No monthly income is assumed. The repayment-to-income ratio is unavailable; cash flow is still calculated.'})
    if scenario.metrics.savings_coverage.value is None:
        messages.append({'code': 'zero_outflows', 'message': 'Listed expenses and repayments total zero, so savings coverage is N/A.'})
    if scenario.key == 'reduced_existing_bnpl':
        messages.append({'code': 'hypothetical_reduction', 'message': 'The reduction is a hypothetical input; it does not change contractual payment obligations.'})
    return messages


def run_simulation(payload, *, income_drop=0.2, bnpl_reduction=0):
    """Return ok/partial/invalid_input, structured metrics, deltas and UI-ready text.

    Numbers are supplied as numeric objects, not strings. income_drop is a fraction
    from 0 to 1. Output numeric values are decimal strings or None, never NaN/inf.
    """
    try:
        inputs, settings = validate_inputs(payload, income_drop=income_drop, bnpl_reduction=bnpl_reduction)
    except SimulationInputError as error:
        return {'status': 'invalid_input', 'errors': [asdict(issue) for issue in error.issues], 'scenarios': []}
    results = compare_scenarios(inputs, settings)
    scenarios = []
    for scenario in results:
        metrics = {name: metric_dict(getattr(scenario.metrics, name)) for name in MonthlyMetrics.__dataclass_fields__}
        deltas = {name: metric_dict(getattr(scenario.deltas, name)) for name in MonthlyMetrics.__dataclass_fields__}
        scenarios.append({'key': scenario.key, 'title': scenario.title,
                          'status': 'partial' if any(m['status']=='unavailable' for m in metrics.values()) else 'ok',
                          'effective_inputs': inputs_dict(scenario.effective_inputs),
                          'metrics': metrics, 'delta_from_current': deltas,
                          'display': {name: display_metric(getattr(scenario.metrics, name)) for name in MonthlyMetrics.__dataclass_fields__},
                          'delta_display': {name: display_metric(getattr(scenario.deltas, name), change=True) for name in MonthlyMetrics.__dataclass_fields__},
                          'applied_changes_from_current': {
                              'income_change': decimal_text(scenario.effective_inputs.I-results[0].effective_inputs.I),
                              'added_bnpl': decimal_text(scenario.effective_inputs.Bnew),
                              'existing_bnpl_reduction': decimal_text(inputs.B0-scenario.effective_inputs.B0)},
                          'assumptions': list(scenario.assumptions), 'messages': rule_notices(scenario)})
    return {'status': 'partial' if any(s['status']=='partial' for s in scenarios) else 'ok',
            'errors': [], 'calculation_type': 'deterministic_monthly_financial_calculation',
            'currency': inputs.currency, 'original_inputs': inputs_dict(inputs),
            'settings': {'income_drop_fraction': decimal_text(settings.income_drop),
                         'income_drop_percent': decimal_text(settings.income_drop*100),
                         'bnpl_reduction': decimal_text(settings.bnpl_reduction)},
            'baseline': 'current', 'delta_convention': 'scenario minus current; ratio deltas are absolute ratio changes, not relative percentage changes',
            'numeric_serialization': 'Decimal strings rounded to 28 significant digits; arithmetic is exact rational. UI values are formatted separately.',
            'limitations': list(LIMITATIONS), 'scenarios': scenarios}
