"""Strict numeric validation for the independent monthly financial simulator."""
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from numbers import Integral, Real
import re

AMOUNT_FIELDS = ('I', 'E', 'D', 'B0', 'Bnew', 'S')


@dataclass(frozen=True)
class InputIssue:
    field: str
    message: str


@dataclass(frozen=True)
class FinancialInputs:
    """Validated exact monetary values, all expressed in one currency."""
    I: Fraction
    E: Fraction
    D: Fraction
    B0: Fraction
    Bnew: Fraction
    S: Fraction
    currency: str = 'AUD'

    def __post_init__(self):
        for field in AMOUNT_FIELDS:
            value = getattr(self, field)
            if not isinstance(value, Fraction) or value < 0:
                raise ValueError('FinancialInputs requires validated nonnegative Fraction values')
        if not re.fullmatch(r'[A-Z]{3}', self.currency):
            raise ValueError('Currency must be a three-letter uppercase label')


@dataclass(frozen=True)
class ScenarioSettings:
    income_drop: Fraction
    bnpl_reduction: Fraction

    def __post_init__(self):
        if not isinstance(self.income_drop, Fraction) or not 0 <= self.income_drop <= 1:
            raise ValueError('Income drop must be a validated fraction in [0, 1]')
        if not isinstance(self.bnpl_reduction, Fraction) or self.bnpl_reduction < 0:
            raise ValueError('BNPL reduction must be validated and nonnegative')


class SimulationInputError(ValueError):
    """Structured validation failure suitable for a later web form."""
    def __init__(self, issues):
        self.issues = tuple(issues)
        super().__init__('; '.join(f'{i.field}: {i.message}' for i in self.issues))


def nonnegative_number(value, field):
    """Do not coerce strings or booleans into monetary values."""
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        raise SimulationInputError([InputIssue(field, 'Enter a finite nonnegative number; strings and booleans are not accepted.')])
    if isinstance(value, Integral):
        result = Fraction(int(value))
    elif isinstance(value, Fraction):
        result = value
    else:
        try:
            number = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise SimulationInputError([InputIssue(field, 'Enter a finite nonnegative number.')]) from None
        if not number.is_finite():
            raise SimulationInputError([InputIssue(field, 'NaN and infinite values are not allowed.')])
        result = Fraction(number)
    if result < 0:
        raise SimulationInputError([InputIssue(field, 'Amount must be nonnegative.')])
    return result


def validate_inputs(payload, *, income_drop=0.2, bnpl_reduction=0):
    """Return immutable validated values or field-specific issues; never alter payload."""
    if not isinstance(payload, Mapping):
        raise SimulationInputError([InputIssue('inputs', 'Provide a mapping of the six monetary inputs.')])
    issues = []; amounts = {}
    for key in payload:
        if key not in (*AMOUNT_FIELDS, 'currency'):
            issues.append(InputIssue(str(key), 'Unknown input field.'))
    for field in AMOUNT_FIELDS:
        if field not in payload:
            issues.append(InputIssue(field, 'This monetary input is required.'))
        else:
            try:
                amounts[field] = nonnegative_number(payload[field], field)
            except SimulationInputError as error:
                issues.extend(error.issues)
    currency = payload.get('currency', 'AUD')
    if isinstance(currency, str) and re.fullmatch(r'[A-Za-z]{3}', currency):
        currency = currency.upper()
    else:
        issues.append(InputIssue('currency', 'Use one three-letter currency label, such as AUD.'))
    settings = {}
    for field, value in [('income_drop', income_drop), ('bnpl_reduction', bnpl_reduction)]:
        try:
            settings[field] = nonnegative_number(value, field)
        except SimulationInputError as error:
            issues.extend(error.issues)
    if 'income_drop' in settings and settings['income_drop'] > 1:
        issues.append(InputIssue('income_drop', 'Use a fraction from 0 to 1 (0% to 100%).'))
    if 'bnpl_reduction' in settings and 'B0' in amounts and settings['bnpl_reduction'] > amounts['B0']:
        issues.append(InputIssue('bnpl_reduction', 'Reduction cannot exceed existing BNPL monthly repayment B0.'))
    if issues:
        raise SimulationInputError(issues)
    return FinancialInputs(**amounts, currency=currency), ScenarioSettings(**settings)
