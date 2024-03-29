from flask_babel import lazy_gettext as _

SECRET_KEY = "fffffffffffffffffffffffffffffffffffffffffff"
SECURITY_PASSWORD_SALT = "000000000000000000000000000000000000000"
SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
}
BOOTSTRAP_SERVE_LOCAL = True
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_REGISTER_USER_TEMPLATE = "register.html"
SECURITY_LOGIN_USER_TEMPLATE = "login.html"
KLIMATICKET_DEFAULT_PRICE = 1095
BABEL_DEFAULT_LOCALE = "de"
LANGUAGES = {"en": "English", "de": "Deutsch"}
DEFAULT_LANGUAGE = "en"
SITE_TITLE = "zug.lol"
SITE_DESCRIPTION = _(
    "Search for train ticket prices in Austria and create a travel journal, to find out if your Klimaticket pays off."
)
SITE_BASE_URI = "https://zug.lol"
SITE_EMAIL = "zug@sad.bz"
RECAPTCHA_SCRIPT = "https://hcaptcha.com/1/api.js"
RECAPTCHA_VERIFY_SERVER = "https://hcaptcha.com/siteverify"
RECAPTCHA_PUBLIC_KEY = "10000000-ffff-ffff-ffff-000000000001"
RECAPTCHA_PRIVATE_KEY = "0x0000000000000000000000000000000000000000"
DEBUG_TB_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
CONTENT_SECURITY_POLICY = {
    "object-src": "'none'",
    "base-uri": "'none'",
    "script-src": [
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
    ],
    "frame-src": [
        "'self'",
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
    ],
    "connect-src": [
        "'self'",
        "https://hcaptcha.com",
        "https://*.hcaptcha.com",
        "https://sentry.io",
    ],
    "report-uri": (
        "https://o4504754043682816.ingest.sentry.io"
        "/api/4504754195267584/security"
        "/?sentry_key=c64aaf9777674f8e9f2a8c67bfb9820e"
    ),
}
CONTENT_SECURITY_POLICY_NONCE_IN = ["script-src"]
FORCE_HTTPS = False
ADMIN_ROLE_NAME = "admin"
MAINTENANCE = False
