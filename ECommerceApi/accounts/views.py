from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, FormView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from rest_framework import viewsets, permissions
from .models import User
from .forms import CustomUserCreationForm
from .serializers import UserSerializer


def accounts_home(request):
    return render(request, 'accounts/account_home.html')

class RegisterView(CreateView):
    """Handles user registration with a form."""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('product-list')
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class LoginView(FormView):
    """Handles user login with a form."""
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('product-list')
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.info(self.request, f'You are now logged in as {username}.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid username or password.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class LogoutView(View):
    """Logs out the authenticated user."""
    template_name = 'template/registration/logout.html'

    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('product-list')
    
    def post(self, request):
        return self.get(request)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Allow anyone to create user, but require auth for other actions."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Additional actions when creating a user."""
        user = serializer.save()
        return user