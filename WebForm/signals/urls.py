from django.urls import path, include
from rest_framework import routers
from .views import SignalViewSet

router = routers.DefaultRouter()
router.register(r'signals', SignalViewSet, basename="signals")

urlpatterns = [
    path('private/', include(router.urls)),
]
