def convert_booleans_to_symbols(dictionary: dict):
    for key, value in dictionary.items():
        if not value_is_boolean(value):
            continue
        if value_is_true(value):
            dictionary[key] = '✓'
        else:
            dictionary[key] = '✗'


def value_is_boolean(value):
    return isinstance(value, bool)


def value_is_true(value):
    return value


def get_boolean_inputs(input_dictionary: dict):
    boolean_inputs = {key: True for key, value in input_dictionary.items() if value == 'on' and key != 'favourite'}
    return boolean_inputs
