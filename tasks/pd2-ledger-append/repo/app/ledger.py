import pandas as pd

COLUMNS = ["date", "account", "amount"]


def build_ledger(entries):
    ledger = pd.DataFrame(columns=COLUMNS)
    for date, account, amount in entries:
        ledger = ledger.append(
            {"date": date, "account": account, "amount": amount}, ignore_index=True
        )
    ledger["amount"] = ledger["amount"].astype(float)
    return ledger


def balance(ledger, account):
    return float(ledger.loc[ledger["account"] == account, "amount"].sum())
