from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from helsinki_gdpr.views import DeletionNotAllowed, DryRunException, GDPRAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import BFIsAuthenticated
from users.api.v1.permissions import BFGDPRScopesPermission
from users.api.v1.serializers import UserSerializer
from users.utils import set_mock_user_name

User = get_user_model()


@extend_schema(
    description="API for retrieving information about the currently logged in user."
)
class CurrentUserView(APIView):

    # TermsOfServiceAccepted is not required here, so that the frontend is able to check if terms
    # approval is required.
    permission_classes = [BFIsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(
            self._get_current_user(request), context={"request": request}
        )
        return Response(serializer.data)

    def _get_current_user(self, request):
        if not request.user.is_authenticated and not settings.NEXT_PUBLIC_MOCK_FLAG:
            raise PermissionDenied
        if settings.NEXT_PUBLIC_MOCK_FLAG and isinstance(request.user, AnonymousUser):
            set_mock_user_name(request.user)
        return request.user


class UserUuidGDPRAPIView(GDPRAPIView):
    """
    GDPR-API view that is used from Helsinki profile to query and delete user data.
    """

    permission_classes = [BFGDPRScopesPermission]
    authentication_classes = []

    def get_object(self) -> AbstractBaseUser:
        """Get user by Helsinki-profile user ID that is stored as username."""
        obj = get_object_or_404(User, username=self.kwargs["uuid"])
        self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, *args, **kwargs):
        """Delete all data related to the given user."""
        try:
            with transaction.atomic():
                user = self.get_object()
                user.delete()
                self.check_dry_run()
        except DryRunException:
            pass
        except DatabaseError:
            raise DeletionNotAllowed()

        return Response(status=status.HTTP_204_NO_CONTENT)
