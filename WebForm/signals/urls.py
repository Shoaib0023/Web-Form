from django.urls import path, include
from rest_framework import routers
from .views import SignalViewSet, attachment

router = routers.DefaultRouter()
router.register(r'signals', SignalViewSet, basename="signals")

urlpatterns = [
    path('private/signals/<int:pk>/attachment', attachment, name="attachments"),
    path('private/', include(router.urls)),
]
