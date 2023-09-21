import os
import hashlib
from typing import Tuple


class CryptPbkdf2:
    HASH_FUNCTION = "sha512"
    SALT_LENGTH = 64
    ITERATIONS = 120000

    @classmethod
    def _generate_salt(cls) -> bytes:
        return os.urandom(cls.SALT_LENGTH)

    @classmethod
    def _hash_password(cls, cleartext_password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            cls.HASH_FUNCTION,
            cleartext_password.encode(),
            salt,
            iterations=cls.ITERATIONS,
        )

    @classmethod
    def encrypt_password(cls, cleartext_password: str) -> Tuple[bytes, bytes]:
        salt = cls._generate_salt()
        hashed_password = cls._hash_password(cleartext_password, salt)
        return hashed_password, salt

    @classmethod
    def check_password(
        cls, cleartext_password: str, hashed_password: bytes, salt: bytes
    ) -> bool:
        return cls._hash_password(cleartext_password, salt) == hashed_password
