from django import forms
from django.contrib.auth.models import User
from .models import Shipment


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'sender_name', 'sender_email', 'sender_phone', 'sender_address', 
            'sender_city', 'sender_postal',
            'receiver_name', 'receiver_email', 'receiver_phone', 'receiver_address',
            'receiver_city', 'receiver_postal',
            'cargo_type', 'cargo_description', 'weight_kg'
        ]
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'sender_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'sender_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'sender_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Street Address'}),
            'sender_city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'sender_postal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Postal Code'}),
            
            'receiver_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'receiver_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'receiver_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'receiver_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Street Address'}),
            'receiver_city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'receiver_postal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Postal Code'}),
            
            'cargo_type': forms.Select(attrs={'class': 'form-input'}),
            'cargo_description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe your cargo...'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Weight in KG', 'step': '0.01'}),
        }
