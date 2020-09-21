from . import workflow
import uuid
from djongo import models
from django.db.models.signals import post_save
import json
import requests
import pika
from django.core.serializers.json import DjangoJSONEncoder
import urllib.request as urllib
import strgen
import string
import random 
from django.utils.text import slugify


PRIORITY_LOW = 'low'
PRIORITY_NORMAL = 'normal'
PRIORITY_HIGH = 'high'
PRIORITY_CHOICES = (
    (PRIORITY_LOW, 'Low'),
    (PRIORITY_NORMAL, 'Normal'),
    (PRIORITY_HIGH, 'High'),
)

MAX_LENGTH = 6

class Signal(models.Model):
    kenmark = models.SlugField(editable=False, default='', max_length=MAX_LENGTH)
    text = models.CharField(max_length=255)

    # ? Location data
    address = models.CharField(max_length=255, null=True, blank=True)
    coordinates = models.CharField(max_length=255, null=True, blank=True)

    # ? Status data
    state = models.CharField(max_length=20, blank=True, choices=workflow.STATUS_CHOICES, default=workflow.GEMELD)

    # ? Reporter data
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    # ? Attachment
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', null=True, blank=True, max_length=255)

    # ? Priority data
    priority = models.CharField(max_length=255, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)

    # ? Department data
    code = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.text}"

    def save(self, *args, **kwargs):
        # s = (''.join(random.choice(string.ascii_uppercase) for x in range(3))).upper()
        kenmark = ''.join(random.choice(string.digits) for x in range(3)) + ''.join(random.choice(string.ascii_uppercase) for x in range(3))
        self.kenmark = kenmark
        super(Signal, self).save(*args, **kwargs)



# ? Publish signal data to queue
def publish_signal_data(sender, instance, **kwargs):
    HOST = 'http://localhost:2222'
    SEDA_HOST = 'http://ec2-52-200-189-81.compute-1.amazonaws.com:8000'
    category_level_name1 = "Afval"
    category_level_name2 = "Afvalbakken"
    category_level_name3 = "Afvalbak"
    category_level_name4 = "Vol"

    coordinates = instance.coordinates
    address = instance.address
    coordinates = json.loads(instance.coordinates)
    address = json.loads(instance.address)
    location = {
        "geometrie" : {"type":"Point","coordinates": coordinates},
        "address" : address
        }

    try:
        data = {
            "text" : instance.text
        }
        response = requests.post('http://52.200.189.81:2000/text_analytics_json', json=data)
        print(response.status_code)
        print(response.json())
        category_level_name1 = response.json()["Hoofdcategorie"]
        category_level_name2 = response.json()["Subcategorie1"]
        category_level_name3 = response.json()["Subcategorie2"]
        category_level_name4 = response.json()["Subcategorie3"]
    except:
        print("Not worked !!!")

    if category_level_name4 and category_level_name4 != "Geen":
        category_url = f"{SEDA_HOST}/signals/v1/public/terms/categories/{category_level_name1}/{category_level_name2}/{category_level_name3}/{category_level_name4}"

    else:
        category_url = f"{SEDA_HOST}/signals/v1/public/terms/categories/{category_level_name1}/{category_level_name2}/{category_level_name3}"

    print(category_url)
    payload = {
        "location": location,
        "category":{"category_url": category_url},
        "reporter":{"phone":instance.phone, "email": instance.email, "sharing_allowed":True},
        "incident_date_start": str(instance.created_at),
        "text": instance.text
    }
    data = json.dumps(payload, indent=4, sort_keys=True, default=str)

    response = requests.post(f"{SEDA_HOST}/signals/v1/public/signals/", json=payload)
    print(response.status_code)
    # print(response.json())

    if response.status_code == 201:
        if instance.file:
            url = f'{HOST}{instance.file.url}'
            img = urllib.urlopen(url)

            data = {
                "signal_id": response.json()["signal_id"]
            }
            res = requests.post(f'{SEDA_HOST}/signals/signal/image/', files={'image': img.read()}, data=data)
            print("Image : ", res.status_code)
            # print(res.json())

post_save.connect(publish_signal_data, sender=Signal)
