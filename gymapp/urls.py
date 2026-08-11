from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import PlanViewSet, OrderViewSet, checkout_view, save_address_view

router = DefaultRouter()
router.register('plans', PlanViewSet, basename='plan')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('api/', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/save-address/', save_address_view, name='save_address'),
]