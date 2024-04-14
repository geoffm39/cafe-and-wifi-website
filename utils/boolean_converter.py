from sqlalchemy import Column
from app.models import Cafe


def convert_booleans_to_symbols(cafe: Cafe):
    for attribute in cafe.__table__.columns:
        if attribute_is_boolean(attribute):
            pass


def attribute_is_boolean(attribute: Column):
    return attribute.type.python_type is bool