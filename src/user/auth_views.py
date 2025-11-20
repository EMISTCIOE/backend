from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView

from src.user.throttling import ForgetPasswordThrottle, LoginThrottle

from .auth_serializers import (
    UserChangePasswordSerializer,
    UserForgetPasswordRequestSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserResetPasswordSerializer,
    UserVerifyAccountSerializer,
)
from .messages import (
    ACCOUNT_VERIFIED,
    LOGOUT_SUCCESS,
    PASSWORD_CHANGED,
    PASSWORD_RESET_LINK_SENT,
    PROFILE_UPDATED,
)
from .models import User
from .schemas import UserLoginResponseSerializer


class UserTokenRefreshView(TokenRefreshView):
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            # Call the parent method to process the request
            return super().post(request, *args, **kwargs)
        except InvalidToken:
            error_message = "Your session has expired. Please log in again to continue."
            return Response(
                {"detail": error_message, "code": "session_expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserLoginView(APIView):
    """View to login a user"""

    permission_classes = [AllowAny]
    authentication_classes = []  # Disable SessionAuthentication/CSRF enforcement for login
    serializer_class = UserLoginSerializer
    throttle_classes = [LoginThrottle]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginResponseSerializer},
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerifyAccountAPIView(APIView):
    """User Verify Account View"""

    permission_classes = [AllowAny]
    serializer_class = UserVerifyAccountSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": ACCOUNT_VERIFIED}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """User LogOut View"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": LOGOUT_SUCCESS}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    """User Profile View"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)


class UserProfileUpdateView(generics.UpdateAPIView):
    """User Profile Update View"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer
    http_method_names = ["patch"]

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            serializer.save()
            return Response({"message": PROFILE_UPDATED}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(APIView):
    """Change Users Password View"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            user = request.user
            new_password = serializer.validated_data.get("new_password")

            # Set new password and save user
            user.set_password(new_password)
            user.save()

            return Response({"message": PASSWORD_CHANGED}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserForgetPasswordRequestView(APIView):
    """Forget Password Request View"""

    permission_classes = [AllowAny]
    serializer_class = UserForgetPasswordRequestSerializer
    throttle_classes = [ForgetPasswordThrottle]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            email = validated_data["email"]
            serializer.save()
            response_message = PASSWORD_RESET_LINK_SENT.format(email=email)
            return Response({"message": response_message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResetPasswordView(APIView):
    """User Reset Password View"""

    permission_classes = [AllowAny]
    serializer_class = UserResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": PASSWORD_CHANGED}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteAccountView(generics.CreateAPIView):
    """User Delete Account View"""

    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                    },
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_archived = True
        user.is_active = False
        user.updated_at = timezone.now()
        user.save()
