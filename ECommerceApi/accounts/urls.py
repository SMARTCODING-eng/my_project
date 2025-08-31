from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-root/', api_root, name='api-root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('docs/', include_docs_urls(title='User API Documentation')),
    path('api-auth/', include('rest_framework.urls')),
    


    ]