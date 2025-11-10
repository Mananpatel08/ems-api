from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PersonalDetails, ServiceDetails, STEP_MODEL_MAPPING


@receiver(post_save, sender=PersonalDetails)
@receiver(post_save, sender=ServiceDetails)
def update_form_step_on_step_complete(sender, instance, **kwargs):
    if not getattr(instance, "is_step_completed", False):
        return

    root_form = getattr(instance, "root_form", None)
    if not root_form:
        return

    current_steps = list(root_form.step_completed or [])
    if not isinstance(current_steps, list):
        current_steps = []

    model_name = sender.__name__
    step_enum = STEP_MODEL_MAPPING.get(model_name)

    if step_enum and step_enum not in current_steps:
        current_steps.append(step_enum)
        root_form.step_completed = current_steps
        root_form.save(update_fields=["step_completed"])
