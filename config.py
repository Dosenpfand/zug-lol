from flask_babel import lazy_gettext as _

# secrets.token_urlsafe()
SECRET_KEY = 'sxnyY8z4wz862Vzzq33GM3yBq09SuSZyHuvHCt9hWh0'
# secrets.SystemRandom().getrandbits(128)
SECURITY_PASSWORD_SALT = '261571404880005318712872279376887086919'
SQLALCHEMY_DATABASE_URI = 'sqlite:///oebb-ticket-price.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
}
BOOTSTRAP_SERVE_LOCAL = True
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_REGISTER_USER_TEMPLATE = 'register.html'
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
# TODO: temporary until translation is fixed
SECURITY_MSG_LOGIN = (_("Please log in to access this page."), "info")
KLIMATICKET_DEFAULT_PRICE = 1095
BABEL_DEFAULT_LOCALE = 'de'
LANGUAGES = {'en': 'English', 'de': 'Deutsch'}
SITE_TITLE = 'zug.lol'
RECAPTCHA_SCRIPT = 'https://hcaptcha.com/1/api.js'
RECAPTCHA_VERIFY_SERVER = 'https://hcaptcha.com/siteverify'
RECAPTCHA_PUBLIC_KEY = '10000000-ffff-ffff-ffff-000000000001'
RECAPTCHA_PRIVATE_KEY = '0x0000000000000000000000000000000000000000'

# TODO: Add to README.md which values should be set in .env
