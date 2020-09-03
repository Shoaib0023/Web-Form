from django.urls import path, include
from rest_framework import routers
from .views import SignalViewSet, attachment

router = routers.DefaultRouter()
router.register(r'private/signals', SignalViewSet, basename="signals")

urlpatterns = [
    path('v1/private/signals/<int:pk>/attachment', attachment, name="attachments"),
    path('v1/', include(router.urls)),
]
