from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from gymapp.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('gymapp.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('signin/', TemplateView.as_view(template_name='signin.html'), name='signin'),
    path('register-step1/', TemplateView.as_view(template_name='register_step1.html'), name='register_step1'),
    path('register-step2/', TemplateView.as_view(template_name='register_step2.html'), name='register_step2'),
]