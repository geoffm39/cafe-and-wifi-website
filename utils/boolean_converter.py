from sqlalchemy import Column
from app.models import Cafe


def convert_booleans_to_symbols(cafe: Cafe):
    for attribute in cafe.__table__.columns:
        if attribute_is_boolean(attribute):
            apply_symbol(cafe, attribute)


def attribute_is_boolean(attribute: Column):
    return attribute.type.python_type is bool


def apply_symbol(cafe: Cafe, attribute: Column):
    value_is_true = getattr(cafe, attribute.name)
    if value_is_true:
        setattr(cafe, attribute.name, '✓')
    else:
        setattr(cafe, attribute.name, '✗')

