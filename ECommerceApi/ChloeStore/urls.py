from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')  
router.register(r'products', ProductViewSet, basename='product')      
router.register(r'orders', OrderViewSet, basename='order')            
router.register(r'payments', PaymentViewSet, basename='payment')      


urlpatterns = [
    path('', store_home, name='store-home'),
    path('', include(router.urls)),
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
]

