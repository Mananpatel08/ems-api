from django.apps import AppConfig


class FormConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "form"

    def ready(self):
        from .signals import update_form_step_on_step_complete as _

        _ = _
