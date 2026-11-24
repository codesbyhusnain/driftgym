from datetime import date
from types import SimpleNamespace

import pytest

from app.bookings import booking_from_dict, booking_from_row


def test_booking_from_dict_cleans_text():
    booking = booking_from_dict({"guest": "  ada lovelace ", "room": " B204 ", "nights": 2, "check_in": "2024-07-01"})
    assert booking.guest == "Ada Lovelace"
    assert booking.room == "B204"
    assert booking.check_in == date(2024, 7, 1)


def test_booking_from_row():
    row = SimpleNamespace(guest="alan turing", room="A101", nights=1, check_in=date(2024, 8, 9))
    assert booking_from_row(row).guest == "Alan Turing"


def test_bookings_are_read_only():
    booking = booking_from_dict({"guest": "grace", "room": "C300", "nights": 3, "check_in": "2024-09-10"})
    with pytest.raises((TypeError, ValueError)):
        booking.nights = 5
