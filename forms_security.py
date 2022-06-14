from flask_babel import lazy_gettext as _
from flask_security import RegisterForm
from flask_wtf import RecaptchaField


class ExtendedRegisterForm(RegisterForm):
    captcha = RecaptchaField(label=_('Prove that you are human'))
