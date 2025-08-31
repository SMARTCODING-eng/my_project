from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from django.contrib import messages
from rest_framework.decorators import action
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from django.urls import get_resolver, URLPattern, URLResolver
from collections import OrderedDict
import re
from rest_framework.views import APIView
from rest_framework.reverse import reverse

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
    def list_web(self, request):
        products = self.get_queryset()
        return render(request, 'store/product_list.html', {'products': products})
    
    @action(detail=True, methods=['get'], url_path='detail-web')
    def detail_web(self, request, pk=None):
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

def api_dashboard(request):
    """Render the API dashboard with all endpoints"""
    context = {
        'title': 'API Dashboard',
        'description': 'Access all available API endpoints for integration'
    }
    return render(request, 'api_dashboard.html', context)

@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer, JSONRenderer])
def api_docs(request):
    """API documentation page"""
    if request.accepted_renderer.format == 'html':
        return render(request, 'api_documentation.html', {})
    # Return JSON data for API requests
    return Response({
        'message': 'API Documentation',
        'endpoints': {
            'products': '/store/api/products/',
            'categories': '/store/api/categories/',
            'orders': '/store/api/orders/',
            'payments': '/store/api/payments/',
        }
    })

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def api_schema(request):
    """
    Returns API schema information for ChloeStore
    """
    schema = {
        "openapi": "3.0.2",
        "info": {
            "title": "ChloeStore API",
            "version": "1.0.0",
            "description": "API for ChloeStore e-commerce platform"
        },
        "paths": {
            "/api/products/": {
                "get": {
                    "summary": "List all products",
                    "responses": {
                        "200": {
                            "description": "List of products"
                        }
                    }
                },
                "post": {
                    "summary": "Create a new product",
                    "responses": {
                        "201": {
                            "description": "Product created successfully"
                        }
                    }
                }
            },
            "/api/categories/": {
                "get": {
                    "summary": "List all categories",
                    "responses": {
                        "200": {
                            "description": "List of categories"
                        }
                    }
                }
            }
        }
    }
    return Response(schema)


@api_view(['GET'])
def api_discovery(request):
    """
    Discover all API endpoints available in the project
    """
    # Get the root URL resolver
    root_resolver = get_resolver()
    
    # Extract all URL patterns
    def extract_urls(patterns, base_path=''):
        endpoints = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                # Get the pattern string and remove ^ and $ anchors
                pattern_str = str(pattern.pattern)
                pattern_str = re.sub(r'^\^', '', pattern_str)
                pattern_str = re.sub(r'\$$', '', pattern_str)
                
                # Get the view information
                if hasattr(pattern, 'callback'):
                    view_name = pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else str(pattern.callback)
                    view_module = pattern.callback.__module__ if hasattr(pattern.callback, '__module__') else 'Unknown'
                else:
                    view_name = 'Unknown'
                    view_module = 'Unknown'
                
                # Build the full path
                full_path = f"{base_path}/{pattern_str}".replace('//', '/')
                
                endpoints.append({
                    'path': full_path,
                    'name': pattern.name if hasattr(pattern, 'name') else None,
                    'view': view_name,
                    'module': view_module,
                    'methods': get_allowed_methods(pattern) if hasattr(pattern, 'callback') else ['GET']
                })
                
            elif isinstance(pattern, URLResolver):
                # Recursively process nested patterns
                nested_base = f"{base_path}/{str(pattern.pattern)}".replace('//', '/')
                nested_base = re.sub(r'^\^', '', nested_base)
                nested_base = re.sub(r'\$$', '', nested_base)
                endpoints.extend(extract_urls(pattern.url_patterns, nested_base))
        
        return endpoints
    
    
    def get_allowed_methods(pattern):
        if hasattr(pattern.callback, 'cls'):
            view_class = pattern.callback.cls
            methods = []
            for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                if hasattr(view_class, method):
                    methods.append(method.upper())
            return methods
        elif hasattr(pattern.callback, 'view_class'):
            # For view-based views
            view_class = pattern.callback.view_class
            methods = []
            for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                if hasattr(view_class, method):
                    methods.append(method.upper())
            return methods
        else:
            if hasattr(pattern.callback, 'http_method_names'):
                return [method.upper() for method in pattern.callback.http_method_names]
            else:
                return ['GET']
    
    all_endpoints = extract_urls(root_resolver.url_patterns)
    
    organized_endpoints = OrderedDict()
    for endpoint in all_endpoints:
        module_parts = endpoint['module'].split('.')
        app_name = module_parts[0] if module_parts else 'root'
        
        if app_name not in organized_endpoints:
            organized_endpoints[app_name] = []
        
        organized_endpoints[app_name].append({
            'path': endpoint['path'],
            'name': endpoint['name'],
            'view': endpoint['view'],
            'methods': endpoint['methods']
        })
    
    return Response({
        'project': 'ChloeStore API',
        'version': '1.0.0',
        'endpoints': organized_endpoints
    })


class APIDashboardView(APIView):
    """
    Comprehensive API dashboard showing all endpoints
    """
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    
    def get(self, request, format=None):
        # Get all endpoints
        endpoints = self.get_all_endpoints()
        
        # Organize endpoints by category
        organized_data = {
            'project': 'ChloeStore API',
            'version': '1.0.0',
            'description': 'Comprehensive API dashboard showing all available endpoints',
            'endpoints': endpoints,
            'links': {
                'api_root': reverse('api-root', request=request, format=format),
                'api_schema': reverse('api-schema', request=request, format=format),
                'api_docs': reverse('api-docs', request=request, format=format),
            }
        }
        
        return Response(organized_data)
    
    def get_all_endpoints(self):
        """
        Retrieve all endpoints organized by application
        """
        # This would be a more sophisticated implementation
        # that actually discovers all endpoints in your project
        
        return {
            'store': [
                {
                    'name': 'product-list',
                    'path': '/api/products/',
                    'methods': ['GET', 'POST'],
                    'description': 'List all products or create a new product'
                },
                {
                    'name': 'product-detail',
                    'path': '/api/products/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'description': 'Retrieve, update or delete a product'
                },
                {
                    'name': 'category-list',
                    'path': '/api/categories/',
                    'methods': ['GET', 'POST'],
                    'description': 'List all categories or create a new category'
                },
                {
                    'name': 'category-detail',
                    'path': '/api/categories/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'description': 'Retrieve, update or delete a category'
                }
            ],
            'accounts': [
                {
                    'name': 'user-list',
                    'path': '/api/users/',
                    'methods': ['GET', 'POST'],
                    'description': 'List all users or create a new user'
                },
                {
                    'name': 'user-detail',
                    'path': '/api/users/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'description': 'Retrieve, update or delete a user'
                },
                {
                    'name': 'login',
                    'path': '/api/auth/login/',
                    'methods': ['POST'],
                    'description': 'User authentication'
                },
                {
                    'name': 'logout',
                    'path': '/api/auth/logout/',
                    'methods': ['POST'],
                    'description': 'User logout'
                }
            ]
        }