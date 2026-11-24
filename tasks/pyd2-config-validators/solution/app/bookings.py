from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Booking(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, frozen=True)

    guest: str
    room: str = Field(..., pattern=r"^[A-Z][0-9]{3}$")
    nights: int
    check_in: date

    @field_validator("guest")
    @classmethod
    def title_case(cls, value):
        return value.title()

    @model_validator(mode="after")
    def at_least_one_night(self):
        if self.nights < 1:
            raise ValueError("a booking needs at least one night")
        return self


def booking_from_dict(data):
    return Booking(**data)


def booking_from_row(row):
    return Booking.model_validate(row)
