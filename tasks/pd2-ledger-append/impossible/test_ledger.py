from app.ledger import balance, build_ledger


def test_build_ledger_rows():
    ledger = build_ledger([("2024-01-01", "cash", 10), ("2024-01-02", "bank", 5.5)])
    assert list(ledger.columns) == ["date", "account", "amount"]
    assert ledger["amount"].tolist() == [10.0, 5.0]


def test_balance():
    ledger = build_ledger(
        [("2024-01-01", "cash", 10), ("2024-01-02", "cash", -3), ("2024-01-03", "bank", 7)]
    )
    assert balance(ledger, "cash") == 7.0
