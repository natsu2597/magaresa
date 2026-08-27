from django.contrib.auth.password_validation import validate_password

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