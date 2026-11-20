import pandas as pd

COLUMNS = ["date", "account", "amount"]


def build_ledger(entries):
    rows = [{"date": d, "account": a, "amount": amt} for d, a, amt in entries]
    ledger = pd.DataFrame(rows, columns=COLUMNS)
    ledger["amount"] = ledger["amount"].astype(float)
    return ledger


def balance(ledger, account):
    return float(ledger.loc[ledger["account"] == account, "amount"].sum())
