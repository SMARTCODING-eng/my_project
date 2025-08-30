from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import  *
from django.contrib import messages
from rest_framework.decorators import action

def store_home(request):
    """Store homepage that displays featured products or redirects to product list"""
    products = Product.objects.all().order_by('-created_at')[:4]
    return render(request, 'store/store_home.html', {'products': products})

def product_list(request):
    """Displays a list of all products."""
    products = Product.objects.all()
    print(f"DEBUG: Found {products.count()} products")
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
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['store_manager', 'owner']

    

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
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'name', 'created_at']
    filterset_fields = ['category', 'stock_quantity']

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset
    

    @action(detail=False, methods=['get'], url_path='list-web')
    def get_web(self, request):
        products = self.get_queryset()
        return render(request, 'store/product_list.html', {'products': products})
    
    @action(detail=True, methods=['get'], url_path='detail-web')
    def detail_web(self, request):
        product = self.get_object()
        return render(request, 'store/product_detail.html', {'product': product})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['id', 'status', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'total_amount', 'status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['store_manager', 'owner']:
            return Order.objects.all().select_related('user')
        return Order.objects.filter(user=user).select_related('user')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        return OrderSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'customer':
            return Payment.objects.filter(order__user=self.request.user)
        return Payment.objects.all()
