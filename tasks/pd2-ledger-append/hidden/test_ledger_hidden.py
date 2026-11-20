from app.ledger import balance, build_ledger


def test_many_rows_keep_order_and_index():
    entries = [(f"2024-02-{i % 28 + 1:02d}", "acct" + str(i % 3), i * 1.25) for i in range(40)]
    ledger = build_ledger(entries)
    assert len(ledger) == 40
    assert list(ledger.index) == list(range(40))
    assert ledger["amount"].tolist() == [i * 1.25 for i in range(40)]
    assert balance(ledger, "acct1") == sum(i * 1.25 for i in range(40) if i % 3 == 1)


def test_empty_ledger():
    ledger = build_ledger([])
    assert len(ledger) == 0
    assert list(ledger.columns) == ["date", "account", "amount"]
    assert balance(ledger, "cash") == 0.0


def test_amounts_are_floats():
    ledger = build_ledger([("2024-03-01", "fees", 3)])
    assert ledger["amount"].dtype == float
    assert balance(ledger, "fees") == 3.0
    assert balance(ledger, "missing") == 0.0
