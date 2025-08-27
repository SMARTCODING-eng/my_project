from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions
from .models import *
from .serializers import  *
from rest_framework import generics, filters, viewsets
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('product-list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """Handles user login with a form."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                return redirect('product-list')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """Logs out the authenticated user."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('product-list')

def product_list(request):
    """Displays a list of all products."""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    """Displays a single product's details."""
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

class IsStoreManagerOrReadOnly(permissions.BasePermission):
    """Custom permissions to allow only store manager to edit product."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['store_manager', 'owner']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStoreManagerOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def perform_create(self, serializer):
        serializer.save()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStoreManagerOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['price', 'name']

    def get_queryset(self):
        queryset = Product.objects.all()
        Category = self.request.query_params.get('category')
        if Category:
            queryset = queryset.filter(category__name__icontains=Category)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['store_manager', 'owner']:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    search_fields = ['id', 'status', 'user__username']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'customer':
            return Payment.objects.filter(order__user=self.request.user)
        return Payment.objects.all()
