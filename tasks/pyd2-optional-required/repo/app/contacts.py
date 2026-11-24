from typing import List, Optional

from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    postcode: Optional[str]


class Contact(BaseModel):
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[Address]
    tags: Optional[List[str]]


def parse_contact(data):
    return Contact(**data)


def to_record(data):
    return parse_contact(data).dict()


def mailing_label(data):
    contact = parse_contact(data)
    lines = [contact.name]
    if contact.address:
        lines.append(contact.address.street)
        lines.append(" ".join(p for p in (contact.address.city, contact.address.postcode) if p))
    return "\n".join(lines)


def reachable(data):
    contact = parse_contact(data)
    return bool(contact.email or contact.phone)
