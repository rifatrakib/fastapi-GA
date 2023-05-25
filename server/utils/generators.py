import hashlib
from random import randbytes


def generate_account_validation_token() -> str:
    token = randbytes(32)
    hashed_code = hashlib.sha256()
    hashed_code.update(token)
    verification_code = hashed_code.hexdigest()
    return verification_code
