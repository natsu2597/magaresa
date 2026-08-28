from django.contrib.auth.password_validation import validate_password

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from django.contrib.auth import authenticate

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "profile_image",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "display_name",
        ]

    def validate(self,attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password" : "Passwords do not match"
            })

        validate_password[attrs["password"]]

        return attrs
    

    def create(self,validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user


class LoginSerializer(serializers.Serializer):
   username = serializers.CharField()
   password = serializers.CharField(
       write_only=True
   )

   def validate(self,attrs):
       username = attrs.get("username")
       password = attrs.get("password")

       user = authenticate(
           username=username,
           password=password
       ) 

       if user is None:
           raise serializers.ValidationError({
               "username" : "User does not exist",
               "password" : "Password is incorrect"
           })

       if not user.is_active:
           raise serializers.ValidationError({
               "username" : "User is not active"
           })

       attrs["user"] = user

       return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "display_name",
            "profile_image",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate_current_password(self,value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Current password is incorrect"
            )

        return value

    def validate(self,attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password" : "Passwords don't match"
            })

        validate_password(
            attrs["new_password"],
            self.context["request"].user
        )

        return attrs
        

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate(self,attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise(serializers.ValidationError(
                {
                    "confirm_password" : "Password don't match"
                }
            ))

        try:
            user_id = urlsafe_base64_decode(
                attrs["uid"]
            ).decode()

            user = User.objects.get(
                pk=user_id
            )

        except(
            User.DoesNotExist,
            ValueError,
            TypeError,
            OverflowError
        ):
            raise serializers.ValidationError(
                "Invalid password reset link"
            )

        if not default_token_generator.check_token(
            user,
            attrs["token"]
        ):
            raise serializers.ValidationError(
                "Invalid or expired reset token"
            )

        validate_password(
            attrs["new_password"],
            user
        )

        attrs["user"] = user

        return attrs

        


