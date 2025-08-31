from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')  
router.register(r'products', views.ProductViewSet, basename='product')      
router.register(r'orders', views.OrderViewSet, basename='order')            
router.register(r'payments', views.PaymentViewSet, basename='payment')      


urlpatterns = [
    path('', include(router.urls)),


    path('', views.store_home, name='store-home'),
    path('products/', views.product_list, name='products-temp'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),

    path('api/dashboard/', views.api_dashboard, name='api-dashboard'),
    path('api/docs/', views.api_docs, name='api-docs'),
    path('api/schema/', views.api_schema, name='api-schema'),
]

