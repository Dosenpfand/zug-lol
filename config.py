from flask_babel import lazy_gettext as _

SECRET_KEY = 'fffffffffffffffffffffffffffffffffffffffffff'
SECURITY_PASSWORD_SALT = '000000000000000000000000000000000000000'
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://zug:zug@localhost:5432/zug"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
}
BOOTSTRAP_SERVE_LOCAL = True
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_REGISTER_USER_TEMPLATE = 'register.html'
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
KLIMATICKET_DEFAULT_PRICE = 1095
BABEL_DEFAULT_LOCALE = 'de'
LANGUAGES = {'en': 'English', 'de': 'Deutsch'}
SITE_TITLE = 'zug.lol'
SITE_DESCRIPTION = _('Search for train ticket prices in Austria and create a travel journal, to find out if your Klimaticket pays off.')
SITE_BASE_URI = 'https://zug.lol'
API_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0'
API_HOST = 'https://shop.oebbtickets.at'
RECAPTCHA_SCRIPT = 'https://hcaptcha.com/1/api.js'
RECAPTCHA_VERIFY_SERVER = 'https://hcaptcha.com/siteverify'
RECAPTCHA_PUBLIC_KEY = '10000000-ffff-ffff-ffff-000000000001'
RECAPTCHA_PRIVATE_KEY = '0x0000000000000000000000000000000000000000'
