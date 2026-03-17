---
title: Loan Amortization
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Interactive loan repayment strategy comparison
---

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

🚀 **[Open Live App on Hugging Face](https://ohmyshedge-loan-amortization.hf.space)**

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/onkarshedge/homeloan/main?urlpath=voila%2Frender%2Floan_amortization.ipynb)

[//]: # ([![Binder]&#40;https://mybinder.org/badge_logo.svg&#41;]&#40;https://mybinder.org/v2/zenodo/10.5281/zenodo.19067385/?urlpath=%2Fdoc%2Ftree%2Floan_amortization.ipynb&#41;)


## Run locally

```bash
pip install -e .
voila loan_amortization.ipynb
```
