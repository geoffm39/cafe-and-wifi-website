import hashlib


REQUEST_URL = 'https://www.gravatar.com/avatar/'
MINIMUM_IMAGE_SIZE = 1
MAXIMUM_IMAGE_SIZE = 2048
DEFAULT_IMAGE_SIZE = 80


def get_hashed_email(email):
    encoded_email = email.encode('utf-8')
    hashed_email = hashlib.md5(encoded_email.lower()).hexdigest()
    return hashed_email


def get_gravatar_url(email, size):
    hashed_email = get_hashed_email(email)
    validated_size = validate_image_size(size)
    return f'{REQUEST_URL}{hashed_email}?s={validated_size}'


def validate_image_size(size):
    if size_is_valid(size):
        return size
    else:
        return DEFAULT_IMAGE_SIZE


def size_is_valid(size):
    return MINIMUM_IMAGE_SIZE <= size <= MAXIMUM_IMAGE_SIZE


def gravatar_url(email, size=100, rating='g', default='retro', force_default=False):
    hash_value = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"
