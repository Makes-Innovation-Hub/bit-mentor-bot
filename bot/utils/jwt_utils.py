import jwt
import datetime
#from bot.setting.config import config
def create_jwt(user_id: str) -> str:
    """
    Creates a JWT for authenticating a Telegram user.

    :param user_id: The Telegram user ID to be included in the JWT payload.
    :return: The generated JWT as a string.

    The JWT payload includes:
    - `telegram_user`: A boolean flag indicating that the token is for a Telegram user.
    - `exp`: Expiration time of the token (1 day from the current time).
    """
    payload = {
        "telegram_user": True,
        "time": int(datetime.datetime.now().timestamp()),
    }
    token = jwt.encode(payload, "c6dd44ecf0e0df4762e7feeeaeb8c463e442120a3caa57d05ef6877f91d62032", algorithm="HS256")
    return token