from django.shortcuts import render
from .models import Signal
from .serializers import SignalSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import base64
from django.core.files.base import ContentFile


# Create your views here.
class SignalViewSet(viewsets.ModelViewSet):
    serializer_class = SignalSerializer
    queryset = Signal.objects.all().order_by('-created_by')
    lookup_field = 'id'

    def list(self, *args, **kwargs):
        signals = Signal.objects.all().order_by('-created_at')
        serializer = SignalSerializer(signals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def retrieve(self, request, id):
        signal = Signal.objects.get(id=id)
        serializer = SignalSerializer(signal)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def create(self, request):
        if "images" in request.data:
            images = request.data["images"]
            endpoint = min(3, len(request.data["images"]))

            for i in range(0, endpoint):
                image = images[i]
                format, imgstr = image.split(';base64,')
                ext = format.split('/')[-1]
                img = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                name = "file" + str(i+1)
                request.data[name] = img


        serializer = SignalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signal = serializer.save()
        # print(signal)

        data = SignalSerializer(signal).data
        return Response(data, status=status.HTTP_201_CREATED)

