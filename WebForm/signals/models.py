from . import workflow
import uuid
from djongo import models
from django.db.models.signals import post_save
import json
import requests
import pika
from django.core.serializers.json import DjangoJSONEncoder
import urllib.request as urllib

PRIORITY_LOW = 'low'
PRIORITY_NORMAL = 'normal'
PRIORITY_HIGH = 'high'
PRIORITY_CHOICES = (
    (PRIORITY_LOW, 'Low'),
    (PRIORITY_NORMAL, 'Normal'),
    (PRIORITY_HIGH, 'High'),
)


class Attachment(models.Model):
    seda_signal_id = models.CharField(max_length=255)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', null=False, blank=False, max_length=255)
    _signal = models.ForeignKey('Signal', null=False, on_delete=models.CASCADE, related_name="attachments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self._signal}"


def publish_attachment_data(sender, instance, **kwargs):
    # host = 'http://localhost:2222'
    host = 'http://ec2-52-200-189-81.compute-1.amazonaws.com:8000'
    url = f'{host}{instance.file.url}'
    img = urllib.urlopen(url)
    # print(url, instance, instance.seda_signal_id)
    data = {
        "signal_id": instance.seda_signal_id
    }
    response = requests.post('http://ec2-52-200-189-81.compute-1.amazonaws.com:8000/signals/signal/image/', files={'image': img.read()}, data=data)
    # ec2-52-200-189-81.compute-1.amazonaws.com
    # print(response.status_code)
    # print(response)
    # print(response.json())

post_save.connect(publish_attachment_data, sender=Attachment)



class Signal(models.Model):
    signal_id = models.UUIDField(default=uuid.uuid4)
    text = models.CharField(max_length=255)

    # ? Location data
    address = models.CharField(max_length=255, null=True, blank=True)
    coordinates = models.CharField(max_length=255, null=True, blank=True)

    # ? Status data
    state = models.CharField(max_length=20, blank=True, choices=workflow.STATUS_CHOICES, default=workflow.GEMELD)

    # ? Category data
    category_level_name1 = models.CharField(max_length=255, null=True, blank=True)
    category_level_name2 = models.CharField(max_length=255, null=True, blank=True)
    category_level_name3 = models.CharField(max_length=255, null=True, blank=True)
    category_level_name4 = models.CharField(max_length=255, null=True, blank=True)

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


# ? Publish signal data to queue
def publish_signal_data(sender, instance, **kwargs):
    category_level_name1 = "Afval"
    category_level_name2 = "Afvalbakken"
    category_level_name3 = "Afvalbak"
    category_level_name4 = "Vol"
    # [4.99054263,52.29994823]
    coordinates = json.loads(instance.coordinates)
    address = json.loads(instance.address)
    location = {
        "geometrie" : {"type":"Point","coordinates": coordinates},
        "address" : address
        }

    # try:
    #     response = requests.post('http://52.200.189.81:2000/json_response', {"text": instance.text})
    #     print(response.status_code)
    #     print(response.json())
    # except:
    #     print("Not worked !!!")

    if category_level_name4:
        category_url = f"http://ec2-52-200-189-81.compute-1.amazonaws.com:8000/signals/v1/public/terms/categories/{category_level_name1}/{category_level_name2}/{category_level_name3}/{category_level_name4}"

    else:
        category_url = f"http://ec2-52-200-189-81.compute-1.amazonaws.com:8000/signals/v1/public/terms/categories/{category_level_name1}/{category_level_name2}/{category_level_name3}"

    payload = {
        "location": location,
        "category":{"category_url": category_url},
        "reporter":{"phone":instance.phone, "email": instance.email, "sharing_allowed":True},
        "incident_date_start": instance.created_at,
        "text": instance.text
    }

    data = json.dumps(payload, indent=4, sort_keys=True, default=str)
    response = requests.post("http://ec2-52-200-189-81.compute-1.amazonaws.com:8000/signals/v1/public/signals/", json=json.loads(data))
    # print(response.status_code)
    # print(response.json())

post_save.connect(publish_signal_data, sender=Signal)
