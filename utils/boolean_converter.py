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


def convert_checkbox_strings_to_booleans(input_dictionary: dict):
    converted_dictionary = {key: True if value == 'on' else False for key, value in input_dictionary.items()}
    return converted_dictionary
