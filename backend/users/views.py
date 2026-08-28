from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, UpdateProfileSerializer, ChangePasswordSerializer, LogoutSerializer

# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message" : "User registered successfully",
                    "user" : UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes= [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
            )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "messgage" : "Login successful",
                "user" : UserSerializer(user).data,
                "access" : str(refresh.access_token),
                "refresh" : str(refresh)
            },
            status=status.HTTP_200_OK
        )



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self,request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
            )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message" : "Profile updated successfully",
                "user" : UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request" : request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {
                "message" : "Password changed successfully"
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        refresh_token = serializer.validated_data["refresh"]

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response(
            {
                "message" : "Logout succesfully"
            },
            status=status.HTTP_200_OK,
        )