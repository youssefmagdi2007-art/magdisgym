from rest_framework import serializers
from .models import Plan, Order

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'slug', 'description', 'price', 'features', 'image_url', 'is_featured']

class OrderSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'plan', 'total', 'payment_status', 'order_status',
                  'payment_method_display', 'delivery_method_display', 'first_name', 'last_name',
                  'email', 'phone', 'address', 'city', 'notes', 'placed_at']

class CreateOrderSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    is_guest = serializers.BooleanField(default=True)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES, default='card')
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_CHOICES, default='home')

    def validate_plan_id(self, value):
        if not Plan.objects.filter(id=value).exists():
            raise serializers.ValidationError('Invalid plan ID.')
        return value