import secrets
import string

# Алфавит Base62 (латинские буквы нижнего и верхнего регистра + цифры)
BASE62_ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length: int = 6) -> str:
    """Генерирует криптографически стойкий случайный код заданной длины.

    6 символов в Base62 дают 62^6 ≈ 56.8 миллиардов уникальных комбинаций.
    """
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))
