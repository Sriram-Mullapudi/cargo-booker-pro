from django.contrib import admin
from .models import Shipment, StatusUpdate


class StatusUpdateInline(admin.TabularInline):
    model = StatusUpdate
    extra = 1
    fields = ('status', 'message', 'location', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'sender_name', 'receiver_name', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'cargo_type', 'created_at')
    search_fields = ('tracking_number', 'sender_name', 'receiver_name', 'sender_email')
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Tracking', {
            'fields': ('tracking_number', 'status')
        }),
        ('Sender Info', {
            'fields': ('sender_name', 'sender_email', 'sender_phone', 'sender_address', 'sender_city', 'sender_postal')
        }),
        ('Receiver Info', {
            'fields': ('receiver_name', 'receiver_email', 'receiver_phone', 'receiver_address', 'receiver_city', 'receiver_postal')
        }),
        ('Cargo & Pricing', {
            'fields': ('cargo_type', 'cargo_description', 'weight_kg', 'cargo_type_price', 'total_price')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at', 'estimated_delivery')
        }),
        ('User', {
            'fields': ('user',)
        })
    )
    
    inlines = [StatusUpdateInline]


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('shipment__tracking_number', 'message')
    readonly_fields = ('created_at',)
