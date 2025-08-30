from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', accounts_home, name='user'),
    path('register/', RegisterView.as_view(template_name='accounts/register.html'), name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls')),

    
    path('api/', include(router.urls)),
]

