from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Shipment, StatusUpdate
from .forms import UserRegistrationForm, ShipmentForm


# ============ Auth Views ============

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


# ============ Public Views ============

def index(request):
    """Landing page with hero section and inline tracking"""
    tracking_number = request.GET.get('tracking', '')
    tracked_shipment = None
    
    if tracking_number:
        tracked_shipment = Shipment.objects.filter(
            tracking_number__iexact=tracking_number
        ).first()
    
    stats = {
        'total_shipments': Shipment.objects.count(),
        'total_delivered': Shipment.objects.filter(status='delivered').count(),
        'total_weight': Shipment.objects.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0,
    }
    
    return render(request, 'index.html', {
        'stats': stats,
        'tracked_shipment': tracked_shipment,
        'tracking_number': tracking_number
    })


def track(request):
    """Public tracking page"""
    tracking_number = request.GET.get('tracking', '')
    shipment = None
    status_updates = []
    
    if tracking_number:
        shipment = Shipment.objects.filter(
            tracking_number__iexact=tracking_number
        ).first()
        
        if shipment:
            status_updates = shipment.status_updates.all()
    
    return render(request, 'track.html', {
        'shipment': shipment,
        'status_updates': status_updates,
        'tracking_number': tracking_number
    })


# ============ Dashboard & Booking ============

@login_required(login_url='login')
def dashboard(request):
    """User dashboard with shipment statistics and list"""
    shipments = request.user.shipments.all()
    
    stats = {
        'total_shipments': shipments.count(),
        'pending': shipments.filter(status='pending').count(),
        'in_transit': shipments.filter(status='in_transit').count(),
        'delivered': shipments.filter(status='delivered').count(),
        'total_spent': sum(s.total_price for s in shipments) if shipments else 0,
    }
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        shipments = shipments.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        shipments = shipments.filter(
            Q(tracking_number__icontains=search_query) |
            Q(sender_name__icontains=search_query) |
            Q(receiver_name__icontains=search_query)
        )
    
    return render(request, 'dashboard.html', {
        'shipments': shipments,
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query
    })


@login_required(login_url='login')
def profile(request):
    """User profile page"""
    shipments = request.user.shipments.all()
    
    stats = {
        'total': shipments.count(),
        'delivered': shipments.filter(status='delivered').count(),
        'total_spent': sum(s.total_price for s in shipments) if shipments else 0,
        'weight': shipments.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0,
    }
    
    recent_shipments = shipments[:5]
    
    return render(request, 'profile.html', {
        'stats': stats,
        'recent_shipments': recent_shipments
    })


@login_required(login_url='login')
def book_shipment(request):
    """Book a new shipment with auto-pricing"""
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.user = request.user
            shipment.calculate_price()
            shipment.status = 'booked'
            shipment.estimated_delivery = timezone.now() + timedelta(days=7)
            shipment.save()
            
            # Create initial status update
            StatusUpdate.objects.create(
                shipment=shipment,
                status='booked',
                message='Shipment booked successfully',
                location='Warehouse'
            )
            
            messages.success(request, f'✓ Shipment booked! Tracking: {shipment.tracking_number}')
            return redirect('shipment_detail', pk=shipment.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ShipmentForm()
    
    return render(request, 'book.html', {'form': form, 'cargo_prices': get_cargo_prices()})


@login_required(login_url='login')
def shipment_detail(request, pk):
    """Shipment detail view with status timeline"""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check permission
    if shipment.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this shipment.')
        return redirect('dashboard')
    
    status_updates = shipment.status_updates.all()
    
    return render(request, 'shipment_detail.html', {
        'shipment': shipment,
        'status_updates': status_updates
    })


@login_required(login_url='login')
def cancel_shipment(request, pk):
    """Cancel a shipment"""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check permission
    if shipment.user != request.user:
        messages.error(request, 'You do not have permission to cancel this shipment.')
        return redirect('dashboard')
    
    # Only allow cancellation for pending/booked shipments
    if shipment.status not in ['pending', 'booked']:
        messages.error(request, 'This shipment cannot be cancelled.')
        return redirect('shipment_detail', pk=pk)
    
    if request.method == 'POST':
        shipment.status = 'cancelled'
        shipment.save()
        
        # Add status update
        StatusUpdate.objects.create(
            shipment=shipment,
            status='cancelled',
            message='Shipment cancelled by user',
            location='System'
        )
        
        messages.success(request, '✓ Shipment has been cancelled.')
        return redirect('dashboard')
    
    return render(request, 'cancel_shipment.html', {'shipment': shipment})


@login_required(login_url='login')
def invoice(request, pk):
    """Generate and display invoice/receipt"""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check permission
    if shipment.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this invoice.')
        return redirect('dashboard')
    
    return render(request, 'invoice.html', {'shipment': shipment})


# ============ AJAX & Utilities ============

@require_http_methods(["GET"])
def calculate_price(request):
    """AJAX endpoint to calculate price based on cargo type and weight"""
    cargo_type = request.GET.get('cargo_type')
    weight = float(request.GET.get('weight', 0))
    
    cargo_prices = get_cargo_prices()
    price_per_kg = cargo_prices.get(cargo_type, 10)
    total_price = price_per_kg * weight
    
    return JsonResponse({
        'price_per_kg': price_per_kg,
        'total_price': round(total_price, 2),
        'currency': 'USD'
    })


def get_cargo_prices():
    """Helper to get cargo type prices"""
    return {
        'documents': 5,
        'fragile': 15,
        'perishable': 20,
        'electronics': 25,
        'furniture': 30,
        'machinery': 50,
        'other': 10,
    }

