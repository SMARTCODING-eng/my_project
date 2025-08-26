from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['__all__']
        read_only_fields = ['id', 'role']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
        

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.userame', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order_id', read_only=True)
    user_username = serializers.CharField(source='order.user.username', read_only=True)
    class Meta:
        model = Payment
        fields = ['__all__']
        read_only_fields = ['amount']

   