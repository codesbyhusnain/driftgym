from app.contacts import mailing_label, reachable, to_record


def test_mailing_label():
    data = {"name": "Ann Lee", "address": {"street": "1 High St", "city": "Leeds", "postcode": "LS1 1AA"}}
    assert mailing_label(data) == "Ann Lee\n1 High St\nLeeds LS1 1AA"


def test_reachable_and_record():
    assert reachable({"name": "Bo", "phone": "0123"})
    assert to_record({"name": "Bo"}) == {"name": "Bo", "email": None, "phone": None, "address": None, "tags": None}
