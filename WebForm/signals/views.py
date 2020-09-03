from django.shortcuts import render
from .models import Signal, Attachment
from .serializers import SignalSerializer, AttachmentSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
class SignalViewSet(viewsets.ModelViewSet):
    queryset = Signal.objects.all().order_by('-created_at')
    serializer_class = SignalSerializer


@api_view(['GET', 'POST'])
def attachment(request, pk):
    signal = Signal.objects.get(id=pk)

    if request.method == "GET":
        attachments = Attachment.objects.filter(_signal=signal).order_by('-created_at')
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        attachment = Attachment()
        attachment._signal = signal
        attachment.file = request.FILES['file']
        attachment.save()
        serializer = AttachmentSerializer(attachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
