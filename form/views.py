from django.db.transaction import atomic
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import (
    RootForm,
    PersonalDetails,
    ServiceDetails,
)
from .serializer import (
    RootFormSerializer,
    RootFormDetailSerializer,
    RootFormListSerializer,
    PersonalDetailsSerializer,
    ServiceDetailsSerializer,
)
from services.utils import get_response


class RootFormViewSet(viewsets.ModelViewSet):
    queryset = RootForm.objects.all()
    serializer_class = RootFormSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RootFormDetailSerializer
        if self.action == "list":
            return RootFormListSerializer
        return RootFormSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return get_response(
                is_success=True,
                message="Root form created successfully",
                data=RootFormDetailSerializer(obj).data,
                status_code=status.HTTP_201_CREATED,
            )
        return get_response(
            is_success=False,
            message=serializer.errors,
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @atomic
    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True, instance=obj)
        if serializer.is_valid():
            obj = serializer.save()
            return get_response(
                is_success=True,
                message="Root form updated successfully",
                data=RootFormDetailSerializer(obj).data,
                status_code=status.HTTP_200_OK,
            )
        return get_response(
            is_success=False,
            message=serializer.errors,
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class PersonalDetailsViewSet(viewsets.ModelViewSet):
    queryset = PersonalDetails.objects.all()
    serializer_class = PersonalDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return get_response(
                is_success=True,
                message="Personal details created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        return get_response(
            is_success=False,
            message="Failed to create personal details",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @atomic
    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True, instance=obj)
        if serializer.is_valid():
            obj = serializer.save()
            return get_response(
                is_success=True,
                message="Personal details updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        return get_response(
            is_success=False,
            message="Failed to update personal details",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @atomic
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True, instance=obj)
        if serializer.is_valid():
            obj = serializer.save()
            return get_response(
                is_success=True,
                message="Personal details updated successfully",
                data=PersonalDetailsSerializer(obj).data,
                status_code=status.HTTP_200_OK,
            )
        return get_response(
            is_success=False,
            message="Failed to update personal details",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ServiceDetailsViewSet(viewsets.ModelViewSet):
    queryset = ServiceDetails.objects.all()
    serializer_class = ServiceDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @atomic
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return get_response(
                is_success=True,
                message="Service details created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        return get_response(
            is_success=False,
            message="Failed to create service details",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @atomic
    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True, instance=obj)
        if serializer.is_valid():
            obj = serializer.save()
            return get_response(
                is_success=True,
                message="Service details updated successfully",
                data=ServiceDetailsSerializer(obj).data,
                status_code=status.HTTP_200_OK,
            )
        return get_response(
            is_success=False,
            message="Failed to update service details",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @atomic
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True, instance=obj)
        if serializer.is_valid():
            obj = serializer.save()
            return get_response(
                is_success=True,
                message="Service details updated successfully",
                data=ServiceDetailsSerializer(obj).data,
                status_code=status.HTTP_200_OK,
            )
        return get_response(
            is_success=False,
            message="Failed to update service details",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
