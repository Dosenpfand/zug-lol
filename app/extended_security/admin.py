import typing
from flask import abort, current_app
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_security import current_user


class AdminSecurityMixIn:
    def is_accessible(self) -> bool:
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.has_role(current_app.config["ADMIN_ROLE_NAME"])
        )

    def inaccessible_callback(self, name: str, **kwargs: typing.Any) -> typing.NoReturn:
        abort(404)


class AdminModelView(AdminSecurityMixIn, ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_view_details = True
    can_export = True
    form_base_class = SecureForm


class ExtendedAdminIndex(AdminSecurityMixIn, AdminIndexView):
    pass
