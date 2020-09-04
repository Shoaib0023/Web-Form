from . import workflow
import uuid
from djongo import models
from django.db.models.signals import post_save
import json
import requests
import pika
from django.core.serializers.json import DjangoJSONEncoder

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


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# ? Publish signal data to queue
def publish_data(sender, instance, **kwargs):
    category_level_name1 = "Afval"
    category_level_name2 = "Afvalbakken"
    category_level_name3 = "Afvalbak"
    category_level_name4 = "Vol"
    coordinates = [4.99054263,52.29994823]
    location = {
        "geometrie" : {"type":"Point","coordinates": coordinates},
        "address" : {"openbare_ruimte":"Anne Kooistrahof", "huisnummer":"1", "postcode": "1106WG", "woonplaats":"Amsterdam"},"stadsdeel":"T"
        }

    if category_level_name4:
        category_url = f"http://localhost:8000/signals/v1/public/terms/categories/{category_level_name1}/{category_level_name2}/{category_level_name3}/{category_level_name4}"
    
    else:
        category_url = f"http://localhost:8000/signals/v1/public/terms/categories/{category_level_name1}/{category_level_name2}/{category_level_name3}"

    
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

# post_save.connect(publish_data, sender=Signal)
