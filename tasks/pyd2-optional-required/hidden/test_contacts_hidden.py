import pytest

from app.contacts import mailing_label, parse_contact, reachable, to_record


def test_only_a_name():
    assert mailing_label({"name": "Cy"}) == "Cy"
    assert not reachable({"name": "Cy"})


def test_address_without_postcode():
    data = {"name": "Dee", "email": "d@x.org", "address": {"street": "2 Low Rd", "city": "York"}}
    assert mailing_label(data) == "Dee\n2 Low Rd\nYork"
    assert to_record(data)["address"] == {"street": "2 Low Rd", "city": "York", "postcode": None}
    assert reachable(data)


def test_explicit_none_and_tags():
    data = {"name": "Eve", "email": None, "phone": None, "tags": ["vip", "new"]}
    assert to_record(data) == {"name": "Eve", "email": None, "phone": None, "address": None, "tags": ["vip", "new"]}
    assert parse_contact({"name": "Eve"}).tags is None


def test_name_and_address_parts_are_still_required():
    with pytest.raises(ValueError):
        parse_contact({"email": "x@y.z"})
    with pytest.raises(ValueError):
        parse_contact({"name": "Fay", "address": {"street": "3 Mill Ln"}})
