from flask import abort, redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView, expose
from flask_security import current_user


class AdminSecurityMixIn:
    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.has_role("admin")
        )

    def inaccessible_callback(self, name, **kwargs):
        return abort(404)


class AdminModelView(AdminSecurityMixIn, ModelView):
    column_display_pk = True
    column_hide_backrefs = False


class ExtendedAdminIndex(AdminSecurityMixIn, AdminIndexView):
    pass
