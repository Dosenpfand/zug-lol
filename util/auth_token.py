import jwt

from app import db
from app.models import AuthToken
from util.oebb import get_access_token


def get_valid_access_token():
    current_token: AuthToken = AuthToken.query.first()

    if current_token and current_token.is_valid():
        return current_token.token

    access_token = get_access_token()
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})
    expires_at = decoded_token["exp"]

    if current_token:
        db.session.delete(current_token)

    new_token = AuthToken(token=access_token, expires_at=expires_at)
    db.session.add(new_token)
    db.session.commit()
    return access_token
