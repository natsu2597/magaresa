from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, LogoutView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path("register/", 
          RegisterView.as_view(),
          name="register"),

    path("login/",
          LoginView.as_view(),
            name="login"),

    path("profile/",
            ProfileView.as_view(),
            name="profile"
         ),

    path("token/refresh/",
            TokenRefreshView.as_view(),
            name="token-refresh"
         ),

    path("change-password/",
            ChangePasswordView.as_view(),
            name="change-password"
         ),

    path("logout/",
            LogoutView.as_view(),
            name="logout"
         ),

    path("forgot-password/",
            ForgotPasswordView.as_view(),
            name="forgot-password"    
         ),

    path("reset-password/",
            ResetPasswordView.as_view(),
            name="reset-password"    
         )
]