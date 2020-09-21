from django.shortcuts import render
from .models import Signal
from .serializers import SignalSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
class SignalViewSet(viewsets.ModelViewSet):
    queryset = Signal.objects.all().order_by('-created_at')
    serializer_class = SignalSerializer
