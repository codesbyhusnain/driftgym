from datetime import date

from pydantic import BaseModel, Field, root_validator, validator


class Booking(BaseModel):
    guest: str
    room: str = Field(..., regex=r"^[A-Z][0-9]{3}$")
    nights: int
    check_in: date

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        allow_mutation = False

    @validator("guest")
    def title_case(cls, value):
        return value.title()

    @root_validator
    def at_least_one_night(cls, values):
        nights = values.get("nights")
        if nights is not None and nights < 1:
            raise ValueError("a booking needs at least one night")
        return values


def booking_from_dict(data):
    return Booking(**data)


def booking_from_row(row):
    return Booking.from_orm(row)
