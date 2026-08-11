from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
import string
import json
import logging
import requests

from .models import User, Profile, Plan, Order
from .serializers import PlanSerializer, OrderSerializer, CreateOrderSerializer

logger = logging.getLogger(__name__)

def home(request):
    plans = Plan.objects.all().order_by('price')
    return render(request, 'index.html', {'plans': plans})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return JsonResponse({'success': False, 'error': 'Email and password required'}, status=400)
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method in ('POST', 'GET'):
        logout(request)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required(login_url='/signin/')
def checkout_view(request):
    plan_id = request.GET.get('plan_id')
    if not plan_id:
        return redirect('/')
    plan = get_object_or_404(Plan, id=plan_id)
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    
    initial_data = {}
    if profile:
        initial_data = {
            'address_line1': profile.address_line1,
            'address_line2': profile.address_line2,
            'compound': profile.compound,
            'building_number': profile.building_number,
            'city': profile.city,
            'area': profile.area,
            'postal_code': profile.postal_code,
            'phone': profile.phone,
        }
    
    # Convert plan to a dictionary (JSON-serializable)
    plan_data = {
        'id': plan.id,
        'name': plan.name,
        'slug': plan.slug,
        'description': plan.description,
        'price': float(plan.price),  # Decimal → float
        'features': plan.features,
        'image_url': plan.image_url,
        'is_featured': plan.is_featured,
    }
    
    # Convert user to a dictionary (JSON-serializable)
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    
    return render(request, 'checkout.html', {
        'plan': plan_data,          # JSON-serializable dict
        'user': user_data,          # JSON-serializable dict
        'initial_data': initial_data,
        'plan_obj': plan,           # Original object (if needed in template)
    })

@csrf_exempt
@login_required(login_url='/signin/')
def save_address_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.address_line1 = data.get('address_line1', '').strip()
        profile.address_line2 = data.get('address_line2', '').strip()
        profile.compound = data.get('compound', '').strip()
        profile.building_number = data.get('building_number', '').strip()
        profile.city = data.get('city', '').strip()
        profile.area = data.get('area', '').strip()
        profile.postal_code = data.get('postal_code', '').strip()
        profile.country = data.get('country', 'Egypt').strip()
        profile.phone = data.get('phone', '').strip()
        profile.save()
        return JsonResponse({'success': True, 'message': 'Address saved!', 'profile': {
            'address_line1': profile.address_line1,
            'address_line2': profile.address_line2,
            'compound': profile.compound,
            'building_number': profile.building_number,
            'city': profile.city,
            'area': profile.area,
            'postal_code': profile.postal_code,
            'country': profile.country,
            'phone': profile.phone,
        }})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]

class OrderViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        plan_id = serializer.validated_data['plan_id']
        plan = get_object_or_404(Plan, id=plan_id)

        with transaction.atomic():
            order_number = f"GYM-{random.randint(10000, 99999)}-{''.join(random.choices(string.digits, k=4))}"
            order = Order.objects.create(
                plan=plan,
                order_number=order_number,
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                email=serializer.validated_data.get('email', ''),
                phone=serializer.validated_data.get('phone', ''),
                address=serializer.validated_data.get('address', ''),
                city=serializer.validated_data.get('city', ''),
                notes=serializer.validated_data.get('notes', ''),
                total=plan.price,
                is_guest=serializer.validated_data.get('is_guest', True),
                payment_method=serializer.validated_data.get('payment_method', 'card'),
                delivery_method=serializer.validated_data.get('delivery_method', 'home'),
            )
            if request.user.is_authenticated:
                order.user = request.user
                order.save()

            try:
                self._send_emails(order, plan)
            except Exception as e:
                logger.error(f"Email error: {e}")

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        order = get_object_or_404(Order, order_number=pk)
        if not request.user.is_authenticated or (order.user and order.user != request.user):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return Response(OrderSerializer(order).data)

    def _send_emails(self, order, plan):
        from_email = settings.DEFAULT_FROM_EMAIL.split('<')[1].rstrip('>') if '<' in settings.DEFAULT_FROM_EMAIL else settings.DEFAULT_FROM_EMAIL

        items = [{'name': plan.name, 'quantity': 1, 'price': str(plan.price), 'total': str(plan.price)}]
        delivery_info = f"Delivery: {order.get_delivery_method_display()}\nAddress: {order.address}, {order.city}"

        # Customer email
        if order.email:
            context = {
                'order': order,
                'items': items,
                'delivery_info': delivery_info,
                'customer_name': f"{order.first_name} {order.last_name}",
                'delivery_days': '3-5 business days',
            }
            html = render_to_string('email/customer_order_confirmation.html', context)
            plain = strip_tags(html)
            data = {
                "sender": {"email": from_email, "name": "Magdi's Gym"},
                "to": [{"email": order.email}],
                "subject": f"Your Order #{order.order_number} is Confirmed!",
                "htmlContent": html,
                "textContent": plain,
            }
            try:
                r = requests.post('https://api.brevo.com/v3/smtp/email',
                                  headers={'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'},
                                  json=data, timeout=10)
                if r.status_code == 201:
                    logger.info(f"Customer email sent to {order.email}")
            except Exception as e:
                logger.error(f"Customer email failed: {e}")

        # Manager emails
        managers = User.objects.filter(is_order_manager=True, is_active=True)
        if managers.exists():
            context = {
                'order': order,
                'items': items,
                'delivery_info': delivery_info,
                'customer_name': f"{order.first_name} {order.last_name}",
                'customer_email': order.email,
                'customer_phone': order.phone,
            }
            html = render_to_string('email/manager_order_notification.html', context)
            plain = strip_tags(html)
            for manager in managers:
                data = {
                    "sender": {"email": from_email, "name": "Magdi's Gym"},
                    "to": [{"email": manager.email}],
                    "subject": f"New Order #{order.order_number} Placed",
                    "htmlContent": html,
                    "textContent": plain,
                }
                try:
                    r = requests.post('https://api.brevo.com/v3/smtp/email',
                                      headers={'api-key': settings.BREVO_API_KEY, 'Content-Type': 'application/json'},
                                      json=data, timeout=10)
                    if r.status_code == 201:
                        logger.info(f"Manager email sent to {manager.email}")
                except Exception as e:
                    logger.error(f"Manager email failed: {e}")