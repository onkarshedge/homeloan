"""Interactive CLI for the loan amortization schedule."""

from tabulate import tabulate

from loan.amortization import build_schedule


def _fmt(value: float) -> str:
    """Format a float as Indian-style currency string."""
    return f"₹{value:>14,.2f}"


def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt).strip())
            if value <= 0:
                print("  ✗ Value must be greater than zero. Try again.")
                continue
            return value
        except ValueError:
            print("  ✗ Invalid input. Please enter a numeric value.")


def get_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if value <= 0:
                print("  ✗ Value must be greater than zero. Try again.")
                continue
            return value
        except ValueError:
            print("  ✗ Invalid input. Please enter a whole number.")


def display_schedule(schedule) -> None:
    """Print the summary and the full amortization table."""
    print("\n" + "=" * 72)
    print("  LOAN AMORTIZATION SCHEDULE")
    print("=" * 72)
    print(f"  Loan Amount      : {_fmt(schedule.principal)}")
    print(f"  Annual Rate      : {schedule.annual_rate:.2f}%")
    print(
        f"  Tenure           : {schedule.tenure_months} months"
        f"  ({schedule.tenure_months / 12:.1f} years)"
    )
    print(f"  Monthly EMI      : {_fmt(schedule.emi)}")
    print(f"  Total Payment    : {_fmt(schedule.total_payment)}")
    print(f"  Total Interest   : {_fmt(schedule.total_interest)}")
    print("=" * 72)

    headers = ["Month", "Opening Balance", "EMI", "Principal", "Interest", "Closing Balance"]
    table = [
        [
            row.month,
            _fmt(row.opening_balance),
            _fmt(row.emi),
            _fmt(row.principal),
            _fmt(row.interest),
            _fmt(row.closing_balance),
        ]
        for row in schedule.rows
    ]

    print(tabulate(table, headers=headers, tablefmt="rounded_outline", stralign="right"))
    print()


def main() -> None:
    print("\n╔══════════════════════════════════╗")
    print("║   Loan Amortization Calculator   ║")
    print("╚══════════════════════════════════╝\n")

    principal = get_positive_float("  Enter Loan Amount (₹)          : ")
    annual_rate = get_positive_float("  Enter Annual Interest Rate (%)  : ")
    tenure_years = get_positive_int("  Enter Tenure (years)            : ")

    tenure_months = tenure_years * 12
    schedule = build_schedule(principal, annual_rate, tenure_months)
    display_schedule(schedule)


if __name__ == "__main__":
    main()

