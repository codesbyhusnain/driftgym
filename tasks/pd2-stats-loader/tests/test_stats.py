from app.stats import load_values, summary

CSV = "latency_ms\n12\n15\n11\n30\n"


def test_load_values():
    values = load_values(CSV)
    assert values.name == "latency_ms"
    assert values.tolist() == [12, 15, 11, 30]


def test_summary():
    assert summary(CSV) == {"count": 4, "mean": 17.0, "spread": 6.5}
