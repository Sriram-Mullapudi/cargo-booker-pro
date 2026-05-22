from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Public
    path('', views.index, name='index'),
    path('track/', views.track, name='track'),
    
    # Dashboard & Booking
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('book/', views.book_shipment, name='book_shipment'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('shipment/<int:pk>/cancel/', views.cancel_shipment, name='cancel_shipment'),
    path('invoice/<int:pk>/', views.invoice, name='invoice'),
    
    # AJAX
    path('api/calculate-price/', views.calculate_price, name='calculate_price'),
]

