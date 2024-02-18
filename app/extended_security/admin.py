import typing
from flask import abort, current_app
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView, expose
from flask_security import current_user

# Note: flask-admin templates do not support strict CSP, so we need to disable it here


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
    export_types = ["csv", "json"]
    # TODO: CSRF validation fails!
    # form_base_class = SecureForm

    @expose("/")
    def index_view(self) -> str:
        return super().index_view()

    index_view.talisman_view_options = {"content_security_policy": None}

    @expose("/new/", methods=("GET", "POST"))
    def create_view(self) -> str:
        return super().create_view()

    create_view.talisman_view_options = {"content_security_policy": None}

    @expose("/edit/", methods=("GET", "POST"))
    def edit_view(self) -> str:
        return super().edit_view()

    edit_view.talisman_view_options = {"content_security_policy": None}

    @expose("/details/")
    def details_view(self) -> str:
        return super().details_view()

    details_view.talisman_view_options = {"content_security_policy": None}


class ExtendedAdminIndex(AdminSecurityMixIn, AdminIndexView):
    @expose()
    def index(self) -> str:
        return super().index()

    index.talisman_view_options = {"content_security_policy": None}
