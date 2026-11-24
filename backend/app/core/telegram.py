import hashlib
import hmac
from urllib.parse import parse_qsl


def _calculate_secret_key(bot_token: str) -> bytes:
    """Секретный ключ = HMAC-SHA256('WebAppData', bot_token)."""
    return hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Проверяет подпись init_data от Telegram Mini App.

    Возвращает словарь с данными пользователя (id, first_name и т.д.)
    или None, если подпись невалидна.
    """
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if received_hash is None:
        return None

    # Сортируем ключи и собираем строку key=value\nkey2=value2
    sorted_items = sorted(parsed.items(), key=lambda x: x[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

    # Вычисляем HMAC от data_check_string
    secret_key = _calculate_secret_key(bot_token)
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # Сравниваем через hmac.compare_digest (защита от timing attack)
    if not hmac.compare_digest(expected_hash, received_hash):
        return None

    # Валидная подпись — возвращаем данные (с hash для полноты)
    parsed["hash"] = received_hash
    return parsed
