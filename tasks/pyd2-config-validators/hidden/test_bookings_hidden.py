from datetime import date
from types import SimpleNamespace

import pydantic
import pytest

from app.bookings import booking_from_dict, booking_from_row


def _data(**changes):
    data = {"guest": "katherine johnson", "room": "D418", "nights": 4, "check_in": "2025-01-20"}
    data.update(changes)
    return data


def test_bad_room_codes():
    for room in ["d418", "D41", "DD418", "D4188", "4180"]:
        with pytest.raises(pydantic.ValidationError):
            booking_from_dict(_data(room=room))
    assert booking_from_dict(_data(room="  Z999  ")).room == "Z999"


def test_at_least_one_night():
    for nights in [0, -2]:
        with pytest.raises(pydantic.ValidationError):
            booking_from_dict(_data(nights=nights))
    assert booking_from_dict(_data(nights=1)).nights == 1


def test_rows_strip_and_title_case_too():
    row = SimpleNamespace(guest="  mary o'neil ", room=" E100", nights=2, check_in=date(2025, 3, 1), extra="ignored")
    booking = booking_from_row(row)
    assert booking.guest == "Mary O'Neil"
    assert booking.room == "E100"


def test_every_field_is_read_only():
    booking = booking_from_dict(_data())
    for field, value in [("guest", "x"), ("room", "A000"), ("check_in", date(2026, 1, 1))]:
        with pytest.raises((TypeError, ValueError)):
            setattr(booking, field, value)
    assert booking.guest == "Katherine Johnson"
