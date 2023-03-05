from typing import Tuple

from flask import render_template
from flask_babel import gettext as _


def page_not_found(e: Exception) -> Tuple[str, int]:
    return render_template("404.html", title=_("Page Not Found")), 404


def internal_server_error(e: Exception) -> Tuple[str, int]:
    return render_template("500.html", title=_("Internal Server Error")), 500
