from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'register', RegisterView, basename='register')
router.register(r'login', LoginView, basename='login')
router.register(r'logout', LogoutView, basename='logout')

urlpatterns = [
    # path('', accounts_home, name='user'),
    # path('accounts/register/', RegisterView.as_view(), name='register'),
    # path('accounts/login/', LoginView.as_view(), name='login'),
    # path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('api-auth/', include('rest_framework.urls')),


    path('', include(router.urls)),
]

