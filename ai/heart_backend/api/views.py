from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth import get_user_model
from .serializers import PredictSerializer, UserRegisterSerializer, HistorySerializer
from .models import History, PredictionHistory
from .personalize import personalize_recommendations, risk_tier
import joblib, json
import numpy as np
import pandas as pd
import os

User = get_user_model()

# Load model AI
MODEL_PATH = "api/model/best_model_calibrated.pkl"
META_PATH = "api/model/meta.json"

model = joblib.load(MODEL_PATH)
meta = json.load(open(META_PATH))

threshold = meta["threshold"]
feature_order = meta["feature_order"]

class RegisterView(APIView):
    def post(self, request):
        ser = UserRegisterSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response({"msg": "Đăng ký thành công"})
        return Response(ser.errors, status=400)


class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PredictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # convert input -> DataFrame
        df_input = pd.DataFrame([data])
        prob = model.predict_proba(df_input)[0][1]
        p = float(prob)

        # risk level + recommendations
        risk = risk_tier(p)
        recommendations = personalize_recommendations(data, p=p)

        # save history
        history = History.objects.create(
            user=request.user,
            input_data=data,
            probability=p,
            risk=risk,
            recommendations=recommendations
        )

        return Response({
            "probability": p,
            "risk": risk,
            "recommendations": recommendations,
            "history_id": history.id
        }, status=200)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = History.objects.filter(user=request.user).order_by("-created_at")
        return Response(HistorySerializer(histories, many=True).data)