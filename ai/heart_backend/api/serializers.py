from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import History, PredictionHistory
from django.contrib.auth import get_user_model
User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "password", "full_name")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class HistorySerializer(serializers.ModelSerializer):
     risk_level = serializers.CharField(source="risk", read_only=True)
     class Meta:
        model = History
        fields = [
            "id",
            "user",
            "input_data",
            "probability",
            "risk_level",              # <- dùng đúng tên field trong model
            "recommendations",
            "created_at",
        ]

class PredictSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    sex = serializers.IntegerField()
    cp = serializers.IntegerField()
    trestbps = serializers.FloatField()
    chol = serializers.FloatField()
    fbs = serializers.IntegerField()
    restecg = serializers.IntegerField()
    thalach = serializers.FloatField()
    exang = serializers.IntegerField()
    oldpeak = serializers.FloatField()
    slope = serializers.IntegerField()
    ca = serializers.FloatField()
    thal = serializers.IntegerField()