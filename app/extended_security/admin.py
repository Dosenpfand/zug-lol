from flask import abort, current_app
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_security import current_user


def user_formatter(view, context, model, name):
    return f"{model.user.email}"


class AdminSecurityMixIn:
    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.has_role(current_app.config["ADMIN_ROLE_NAME"])
        )

    def inaccessible_callback(self, name, **kwargs):
        return abort(404)


class AdminModelView(AdminSecurityMixIn, ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_view_details = True
    can_export = True
    form_base_class = SecureForm
    column_formatters = dict(user=user_formatter)


class ExtendedAdminIndex(AdminSecurityMixIn, AdminIndexView):
    pass
