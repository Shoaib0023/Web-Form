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
import base64
from urllib.parse import urlparse 
from os.path import splitext
import uuid


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
    text = models.CharField(max_length=1000)

    # ? Location data
    address = models.CharField(max_length=1000, null=True, blank=True)
    coordinates = models.CharField(max_length=255, null=True, blank=True)

    # ? Status data
    state = models.CharField(max_length=20, blank=True, choices=workflow.STATUS_CHOICES, default=workflow.GEMELD)

    # ? Reporter data
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    # ? Attachment
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', null=True, blank=True, max_length=255)
    file1 = models.FileField(upload_to='attachments/%Y/%m/%d/', null=True, blank=True)
    file2 = models.FileField(upload_to='attachments/%Y/%m/%d/', null=True, blank=True)
    file3 = models.FileField(upload_to='attachments/%Y/%m/%d/', null=True, blank=True)

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
        # s = (''.join(random.choice(string.ascii_uppercase) for x in range(3))).upper(
        while True:
            kenmark = ''.join(random.choice(string.digits) for x in range(3)) + ''.join(random.choice(string.ascii_uppercase) for x in range(3))
            if not Signal.objects.filter(kenmark=kenmark).exists():
                break

        self.kenmark = kenmark
        super(Signal, self).save(*args, **kwargs)



# ? Publish signal data to queue
def publish_signal_data(sender, instance, **kwargs):
    HOST = 'http://3.126.254.35:8001'
    SEDA_HOST = 'http://3.126.254.35:8000'
    category_level_name1 = "Afval"
    category_level_name2 = "Afvalbakken"
    category_level_name3 = "Afvalbak"
    category_level_name4 = "Vol"

    coordinates = instance.coordinates
    address = instance.address
    coordinates = json.loads(instance.coordinates)
    address = json.loads(instance.address)
 
    postcode = address["postcode"]
    postcode = ''.join(postcode.split())
    print("PostCode ", postcode)

    if "huisnummer" in address:
        huisnummer = address["huisnummer"]
        payload = {"postcode": postcode, "huisnummer": huisnummer}
    else:
        payload = {"postcode": postcode}

    res = requests.post(f'{SEDA_HOST}/signals/v1/private/get_stadsdeel', data=payload)
    print("Stadsdeel api response code : ", res.status_code)
    if res.status_code == 200:
        stadsdeel = res.json()["stadsdeel"]["name"]
    else:
        stadsdeel = ""

    print("Stadsdeel : ", stadsdeel)

    if stadsdeel != '':
        location = {
             "geometrie" : {"type":"Point","coordinates": coordinates},
             "address" : address,
             "stadsdeel": stadsdeel
         }
    else:
        location = {
             "geometrie" : {"type":"Point","coordinates": coordinates},
             "address" : address
         }

    try:
        data = {
            "text" : instance.text
        }
        response = requests.post('http://52.200.189.81:2000/text_analytics_json', json=data)
        #print(response.status_code)
        #print(response.json())
        category_level_name1 = response.json()["Hoofdcategorie"]
        category_level_name2 = response.json()["Subcategorie1"]
        category_level_name3 = response.json()["Subcategorie2"]
        category_level_name4 = response.json()["Subcategorie3"]

        if category_level_name1 == "Afval" and category_level_name2 == "Grofvuil" and category_level_name3 == "Niet Opgehaald":
            category_level_name1 = "Other"
            category_level_name2 = "Other"
            category_level_name3 = "Other"
            category_level_name4 = "Geen"

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
        "text": instance.text,
        "source": "Melding Doen"
    }
    data = json.dumps(payload, indent=4, sort_keys=True, default=str)
    #print("Data : ", data)

    response = requests.post(f"{SEDA_HOST}/signals/v1/public/signals/", json=payload)
    print(response.status_code)
    print(response.json())

    if response.status_code == 201:
        print("Signals Created in SEDA -- ", response.status_code)

        if instance.file:
            url = f'{HOST}{instance.file.url}'
            path = urlparse(url).path
            ext = splitext(path)[1]
            # print("Ext : ", ext)

            img = urllib.urlopen(url)
            imgHeaders = img.headers
            # print(imgHeaders)

            name = str(uuid.uuid4()) + ext
            seda_id = response.json()["signal_id"]
            files = {'file': (name, img.read(), img.headers["Content-Type"])}
            res = requests.post(f'{SEDA_HOST}/signals/v1/public/signals/{seda_id}/attachments', files=files)
            print("Image : ", res.status_code)

        if instance.file1:
            url = f'{HOST}{instance.file1.url}'
            path = urlparse(url).path
            ext = splitext(path)[1]
            # print("Ext : ", ext)

            img = urllib.urlopen(url)
            imgHeaders = img.headers
            # print(imgHeaders)

            name = str(uuid.uuid4()) + ext
            seda_id = response.json()["signal_id"]
            files = {'file': (name, img.read(), img.headers["Content-Type"])}
            res = requests.post(f'{SEDA_HOST}/signals/v1/public/signals/{seda_id}/attachments', files=files)
            print("Image1 : ", res.status_code)


        if instance.file2:
            url = f'{HOST}{instance.file2.url}'
            path = urlparse(url).path
            ext = splitext(path)[1]
            # print("Ext : ", ext)

            img = urllib.urlopen(url)
            imgHeaders = img.headers
            # print(imgHeaders)

            name = str(uuid.uuid4()) + ext
            seda_id = response.json()["signal_id"]
            files = {'file': (name, img.read(), img.headers["Content-Type"])}
            res = requests.post(f'{SEDA_HOST}/signals/v1/public/signals/{seda_id}/attachments', files=files)
            print("Image2 : ", res.status_code)


        if instance.file3:
            url = f'{HOST}{instance.file3.url}'
            path = urlparse(url).path
            ext = splitext(path)[1]
            img = urllib.urlopen(url)
            imgHeaders = img.headers

            name = str(uuid.uuid4()) + ext
            seda_id = response.json()["signal_id"]

            files = {'file': (name, img.read(), img.headers["Content-Type"])}
            res = requests.post(f'{SEDA_HOST}/signals/v1/public/signals/{seda_id}/attachments', files=files)
            print("Image3 : ", res.status_code)


        data = {
            "webform_kenmark": instance.kenmark
        }

        seda_id = response.json()["signal_id"]
        response = requests.put(f'{SEDA_HOST}/signals/v1/public/signals/{seda_id}', json=data)
        print(response.status_code)
        print("-------------------------------------------") 

post_save.connect(publish_signal_data, sender=Signal)
