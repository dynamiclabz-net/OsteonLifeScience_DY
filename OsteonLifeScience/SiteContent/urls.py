from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'home-page-api', HomePageViewSet, basename='home-page-api')
router.register(r'site-setting-api', SiteSettingViewSet, basename='site-setting-api')

urlpatterns = [
    path('', include(router.urls)),
]
