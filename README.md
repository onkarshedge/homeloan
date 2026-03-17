# 🏦 Loan Amortization — Interactive Strategy Comparison

An interactive Voilà notebook comparing four home loan repayment strategies:

| # | Strategy | Description |
|---|----------|-------------|
| 1 | **Regular** | Pay only the EMI — no extra payments, full original tenure |
| 2 | **Prepayment** | Annual lump-sum prepayments to close the loan in a target tenure |
| 3 | **OD + Prepayment** | Park money in an overdraft account AND make annual prepayments |
| 4 | **OD Only** | Park money in an overdraft account, no prepayments |

Includes opportunity cost analysis — what if you invested the money in the markets instead?

## Launch

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/YOUR_USERNAME/loan-amortization/HEAD?urlpath=voila%2Frender%2Floan_amortization.ipynb)

> Replace `YOUR_USERNAME` with your GitHub username after pushing.

## Run locally

```bash
pip install -e ".[dev]"
voila loan_amortization.ipynb
```

