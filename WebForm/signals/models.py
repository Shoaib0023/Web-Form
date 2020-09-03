# from django.db import models
from . import workflow
import uuid
from djongo import models

PRIORITY_LOW = 'low'
PRIORITY_NORMAL = 'normal'
PRIORITY_HIGH = 'high'
PRIORITY_CHOICES = (
    (PRIORITY_LOW, 'Low'),
    (PRIORITY_NORMAL, 'Normal'),
    (PRIORITY_HIGH, 'High'),
)


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', null=False, blank=False, max_length=255)
    _signal = models.ForeignKey('Signal', null=False, on_delete=models.CASCADE, related_name="attachments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self._signal}"


class Signal(models.Model):
    signal_id = models.UUIDField(default=uuid.uuid4)
    text = models.CharField(max_length=255)

    # ? Location data
    address = models.CharField(max_length=255, null=True, blank=True)
    coordinates = models.CharField(max_length=255, null=True, blank=True)

    # ? Status data
    state = models.CharField(max_length=20, blank=True, choices=workflow.STATUS_CHOICES, default=workflow.GEMELD)

    # ? Category data
    category_level_name1 = models.CharField(max_length=255)
    category_level_name2 = models.CharField(max_length=255)
    category_level_name3 = models.CharField(max_length=255)
    category_level_name4 = models.CharField(max_length=255)

    # ? Reporter data
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    # ? Priority data
    priority = models.CharField(max_length=255, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)

    # ? Department data
    code = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.text}"
