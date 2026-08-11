from django.contrib import admin
from .models import User, Profile, Plan, Order

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'plan', 'total', 'order_status', 'payment_status', 'placed_at']
    list_filter = ['order_status', 'payment_status', 'payment_method']
    search_fields = ['order_number', 'user__email', 'first_name', 'last_name']
    readonly_fields = ['order_number', 'total', 'placed_at']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_order_manager']
    list_filter = ['is_staff', 'is_order_manager']
    search_fields = ['username', 'email']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'area', 'phone']
    search_fields = ['user__username', 'city', 'area']