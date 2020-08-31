
import base64


def get_base64_image(data: str):
    if data.count(';base64,') == 0:
        return None

    try:
        return base64.b64decode(data.split(';base64,')[1])
    except (IndexError, TypeError, ValueError):
        return
