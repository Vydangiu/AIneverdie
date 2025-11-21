from django.urls import path
from .views import RegisterView, PredictView, HistoryView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path("register", RegisterView.as_view()),
#     path("login", TokenObtainPairView.as_view()),
#     path("refresh", TokenRefreshView.as_view()),

#     path("predict", PredictView.as_view()),
#     path("history", HistoryView.as_view()),
# ]

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('predict/', PredictView.as_view(), name='predict'),
    path('history/', HistoryView.as_view(), name='history'),
]