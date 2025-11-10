from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from django.db.transaction import set_rollback
from .models import (
    RootForm,
    PersonalDetails,
    ServiceDetails,
    ExamDetail,
    FormStep,
)


def update_current_step(root_form, step):
    root_form.current_step = step
    root_form.save()
    return root_form


class RootFormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RootForm
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class RootFormStepBaseSerializer(serializers.ModelSerializer):
    root_form = RootFormListSerializer(write_only=True, required=False)
    root_form_id = serializers.PrimaryKeyRelatedField(
        queryset=RootForm.objects.all(), write_only=True, required=False
    )

    class Meta:
        fields = "__all__"
        extra_kwargs = {"root_form": {"required": False}}
        next_step = FormStep.SERVICE_DETAILS

    def update_current_step(self, root_form):
        if self.Meta.next_step == FormStep.SERVICE_DETAILS:
            root_form.status = RootForm.Status.COMPLETED
            root_form.completed_at = now()
        root_form.current_step = self.Meta.next_step
        root_form.save()
        return root_form


class PersonalDetailsSerializer(RootFormStepBaseSerializer):
    class Meta(RootFormStepBaseSerializer.Meta):
        model = PersonalDetails
        next_step = FormStep.SERVICE_DETAILS

    def validate(self, attrs):
        if attrs.get("is_step_completed"):
            required_fields = [
                "email",
                "first_name",
                "middle_name",
                "last_name",
                "gender",
                "mobile_number",
                "pan_number",
            ]
            missing_fields = [
                field for field in required_fields if attrs.get(field, None) is None
            ]
            if missing_fields and not self.instance:
                raise serializers.ValidationError(
                    {
                        field: "This field is required when completing the step."
                        for field in missing_fields
                    }
                )

        return attrs

    def create(self, validated_data):
        user = self.context["user"]
        with transaction.atomic():
            validated_data["created_by"] = user
            root_form = validated_data.pop("root_form_id")
            validated_data["root_form"] = root_form
            personal_details = PersonalDetails.objects.create(**validated_data)
            self.update_current_step(root_form=root_form)

        return personal_details

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self.update_current_step(root_form=instance.root_form)

        return super().update(instance, validated_data=validated_data)


class ExamDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDetail
        fields = ["exam_type", "passing_date", "attempt_count"]
        read_only_fields = ["service_details"]


class ServiceDetailsSerializer(RootFormStepBaseSerializer):
    exams = ExamDetailSerializer(many=True)

    class Meta(RootFormStepBaseSerializer.Meta):
        model = ServiceDetails

    def create(self, validated_data):
        exams = validated_data.pop("exams", [])
        user = self.context["user"]

        with transaction.atomic():
            validated_data["created_by"] = user
            root_form = validated_data.pop("root_form_id")
            validated_data["root_form"] = root_form
            existing_step = ServiceDetails.objects.filter(root_form=root_form).first()
            if existing_step:
                ExamDetail.all_objects.filter(service_details=existing_step).delete()
                existing_step.delete()

            service_details = ServiceDetails.objects.create(**validated_data)

            ExamDetail.objects.bulk_create(
                [ExamDetail(service_details=service_details, **exam) for exam in exams]
            )
            self.update_current_step(root_form=root_form)

        return service_details

    def update(self, instance, validated_data):
        exams = validated_data.pop("exams", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if exams is not None:
            instance.exams.all().delete()
            ExamDetail.objects.bulk_create(
                [ExamDetail(service_details=instance, **exam) for exam in exams]
            )

        self.update_current_step(root_form=instance.root_form)
        return super().update(instance=instance, validated_data=validated_data)


class RootFormSerializer(serializers.ModelSerializer):
    personal_details = PersonalDetailsSerializer(required=False)

    class Meta:
        model = RootForm
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["user"]
        personal_details = validated_data["personal_details"]
        root_form = RootForm.objects.create(
            created_by=user, user=user, status=RootForm.Status.IN_PROGRESS
        )
        personal_details["root_form_id"] = root_form.pk
        personal_details_serializer = PersonalDetailsSerializer(
            data=personal_details, context={"user": user}
        )
        if not personal_details_serializer.is_valid():
            set_rollback(True)
            raise serializers.ValidationError(personal_details_serializer.errors)
        personal_details_serializer.create(
            validated_data=personal_details_serializer.validated_data
        )

        return root_form


class RootFormDetailSerializer(serializers.ModelSerializer):
    personal_details = PersonalDetailsSerializer()
    service_details = ServiceDetailsSerializer()

    class Meta:
        model = RootForm
        fields = "__all__"
