from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'category-api', CategoryViewSet, basename='category-api')
router.register(r'sub-category-api', SubCategoryViewSet, basename='sub-category-api')
router.register(r'product-api', ProductViewSet, basename='product-api')

urlpatterns = [
    path('', include(router.urls)),
]
