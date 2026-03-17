"""Loan amortization schedule calculator."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PaymentRow:
    """Represents a single EMI payment in the amortization schedule."""

    month: int
    opening_balance: float
    emi: float
    principal: float
    interest: float
    closing_balance: float
    prepayment: float = 0.0


@dataclass
class AmortizationSchedule:
    """Full amortization schedule for a loan."""

    principal: float
    annual_rate: float
    tenure_months: int
    emi: float
    total_payment: float
    total_interest: float
    rows: List[PaymentRow] = field(default_factory=list)


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate the Equated Monthly Installment (EMI).

    Formula: EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)

    Args:
        principal:      Loan amount (₹)
        annual_rate:    Annual interest rate in percentage (e.g. 8.5 for 8.5%)
        tenure_months:  Loan tenure in months

    Returns:
        Monthly EMI amount rounded to 2 decimal places.
    """
    if annual_rate == 0:
        return round(principal / tenure_months, 2)

    monthly_rate = annual_rate / 12 / 100
    factor = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * factor / (factor - 1)
    return round(emi, 2)


def build_schedule(
    principal: float, annual_rate: float, tenure_months: int
) -> AmortizationSchedule:
    """
    Build a full month-by-month amortization schedule.

    Args:
        principal:      Loan amount
        annual_rate:    Annual interest rate in percentage
        tenure_months:  Loan tenure in months

    Returns:
        AmortizationSchedule containing every payment row and summary totals.
    """
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12 / 100

    rows: List[PaymentRow] = []
    balance = principal

    for month in range(1, tenure_months + 1):
        opening_balance = balance
        interest = round(balance * monthly_rate, 2)
        principal_component = round(emi - interest, 2)

        # Last month: clear any rounding residue
        if month == tenure_months:
            principal_component = round(balance, 2)
            emi_actual = round(principal_component + interest, 2)
        else:
            emi_actual = emi

        closing_balance = round(opening_balance - principal_component, 2)
        # Guard against floating-point tiny negatives in final month
        closing_balance = max(closing_balance, 0.0)

        rows.append(
            PaymentRow(
                month=month,
                opening_balance=opening_balance,
                emi=emi_actual,
                principal=principal_component,
                interest=interest,
                closing_balance=closing_balance,
            )
        )
        balance = closing_balance

    total_payment = round(sum(r.emi for r in rows), 2)
    total_interest = round(sum(r.interest for r in rows), 2)

    return AmortizationSchedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        emi=emi,
        total_payment=total_payment,
        total_interest=total_interest,
        rows=rows,
    )


def build_schedule_with_prepayments(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    prepayments: Dict[int, float],
) -> AmortizationSchedule:
    """
    Build an amortization schedule that accounts for lump-sum part payments.

    Part payments reduce the outstanding principal immediately.  The EMI stays
    the same, so the loan gets paid off *earlier* (tenure reduction strategy).

    Args:
        principal:      Original loan amount.
        annual_rate:    Annual interest rate in percentage.
        tenure_months:  Original loan tenure in months.
        prepayments:    Mapping of ``{month_number: prepayment_amount}``.
                        The prepayment is applied *after* that month's regular
                        EMI.  E.g. ``{24: 500000}`` means ₹5,00,000 extra is
                        paid at the end of month 24.

    Returns:
        AmortizationSchedule with the effective (shorter) tenure.
    """
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12 / 100

    rows: List[PaymentRow] = []
    balance = principal

    for month in range(1, tenure_months + 1):
        if balance <= 0:
            break

        opening_balance = balance
        interest = round(balance * monthly_rate, 2)
        principal_component = round(emi - interest, 2)

        # If remaining balance is less than the principal component of EMI
        if principal_component >= balance:
            principal_component = round(balance, 2)
            emi_actual = round(principal_component + interest, 2)
            closing_balance = 0.0
        else:
            emi_actual = emi
            closing_balance = round(opening_balance - principal_component, 2)

        # Apply prepayment after EMI
        prepayment = 0.0
        if month in prepayments and closing_balance > 0:
            prepayment = min(prepayments[month], closing_balance)
            prepayment = round(prepayment, 2)
            closing_balance = round(closing_balance - prepayment, 2)

        closing_balance = max(closing_balance, 0.0)

        rows.append(
            PaymentRow(
                month=month,
                opening_balance=opening_balance,
                emi=emi_actual,
                principal=principal_component,
                interest=interest,
                closing_balance=closing_balance,
                prepayment=prepayment,
            )
        )
        balance = closing_balance

    total_payment = round(sum(r.emi + r.prepayment for r in rows), 2)
    total_interest = round(sum(r.interest for r in rows), 2)

    return AmortizationSchedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=len(rows),
        emi=emi,
        total_payment=total_payment,
        total_interest=total_interest,
        rows=rows,
    )


def build_schedule_with_overdraft(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    od_balance: float,
) -> AmortizationSchedule:
    """
    Build an amortization schedule for a home-loan overdraft (OD) account.

    In an OD facility the interest rate is typically higher, but any amount
    parked in the linked OD account offsets the principal for interest
    calculation.  The EMI is computed at the OD rate on the full principal,
    but each month interest is charged only on
    ``max(outstanding_balance - od_balance, 0)``.  Because the effective
    interest is lower, more of each EMI goes towards principal and the loan
    closes earlier.

    Args:
        principal:      Original loan amount.
        annual_rate:    OD annual interest rate in percentage (e.g. 7.55).
        tenure_months:  Original loan tenure in months.
        od_balance:     Constant amount kept parked in the OD account.

    Returns:
        AmortizationSchedule reflecting the reduced-interest, shorter tenure.
    """
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12 / 100

    rows: List[PaymentRow] = []
    balance = principal

    for month in range(1, tenure_months + 1):
        if balance <= 0:
            break

        opening_balance = balance
        effective_balance = max(balance - od_balance, 0.0)
        interest = round(effective_balance * monthly_rate, 2)
        principal_component = round(emi - interest, 2)

        # If remaining balance is less than the principal component of EMI
        if principal_component >= balance:
            principal_component = round(balance, 2)
            emi_actual = round(principal_component + interest, 2)
            closing_balance = 0.0
        else:
            emi_actual = emi
            closing_balance = round(opening_balance - principal_component, 2)

        closing_balance = max(closing_balance, 0.0)

        rows.append(
            PaymentRow(
                month=month,
                opening_balance=opening_balance,
                emi=emi_actual,
                principal=principal_component,
                interest=interest,
                closing_balance=closing_balance,
            )
        )
        balance = closing_balance

    total_payment = round(sum(r.emi for r in rows), 2)
    total_interest = round(sum(r.interest for r in rows), 2)

    return AmortizationSchedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=len(rows),
        emi=emi,
        total_payment=total_payment,
        total_interest=total_interest,
        rows=rows,
    )


def build_schedule_with_od_and_prepayments(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    od_balance: float,
    prepayments: Dict[int, float],
) -> AmortizationSchedule:
    """
    Build an amortization schedule combining OD offset and lump-sum prepayments.

    Interest each month is charged on ``max(outstanding - od_balance, 0)``,
    and any prepayment is applied *after* that month's EMI.

    Args:
        principal:      Original loan amount.
        annual_rate:    OD annual interest rate in percentage.
        tenure_months:  Original loan tenure in months.
        od_balance:     Constant amount parked in the OD account.
        prepayments:    Mapping of ``{month_number: prepayment_amount}``.

    Returns:
        AmortizationSchedule reflecting combined OD + prepayment effects.
    """
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12 / 100

    rows: List[PaymentRow] = []
    balance = principal

    for month in range(1, tenure_months + 1):
        if balance <= 0:
            break

        opening_balance = balance
        effective_balance = max(balance - od_balance, 0.0)
        interest = round(effective_balance * monthly_rate, 2)
        principal_component = round(emi - interest, 2)

        if principal_component >= balance:
            principal_component = round(balance, 2)
            emi_actual = round(principal_component + interest, 2)
            closing_balance = 0.0
        else:
            emi_actual = emi
            closing_balance = round(opening_balance - principal_component, 2)

        # Apply prepayment after EMI
        prepayment = 0.0
        if month in prepayments and closing_balance > 0:
            prepayment = min(prepayments[month], closing_balance)
            prepayment = round(prepayment, 2)
            closing_balance = round(closing_balance - prepayment, 2)

        closing_balance = max(closing_balance, 0.0)

        rows.append(
            PaymentRow(
                month=month,
                opening_balance=opening_balance,
                emi=emi_actual,
                principal=principal_component,
                interest=interest,
                closing_balance=closing_balance,
                prepayment=prepayment,
            )
        )
        balance = closing_balance

    total_payment = round(sum(r.emi + r.prepayment for r in rows), 2)
    total_interest = round(sum(r.interest for r in rows), 2)

    return AmortizationSchedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=len(rows),
        emi=emi,
        total_payment=total_payment,
        total_interest=total_interest,
        rows=rows,
    )
