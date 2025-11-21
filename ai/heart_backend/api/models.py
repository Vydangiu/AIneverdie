from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = models.CharField(max_length=150,blank=True)
    # Username, password, email có sẵn
    pass


class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_data = models.JSONField()   # dữ liệu đầu vào
    probability = models.FloatField()  # xác suất
    risk_level = models.CharField(max_length=50)  # thấp / trung bình / cao
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="histories")
    input_data = models.JSONField()   # lưu raw input của user
    probability = models.FloatField()
    risk = models.CharField(max_length=20)
    recommendations = models.JSONField()  # list recommendations trả ra FE
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History #{self.id} - {self.user.username}"