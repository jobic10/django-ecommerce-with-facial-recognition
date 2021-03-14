from .models import ShippingAddress, Customer
from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class ShippingForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address...'}))
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'City...'}))

    class Meta:
        model = ShippingAddress
        fields = ('address', 'city')


class CustomerForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TextInput(
        attrs={'autofocus': 'autofocus', 'class': 'form-control', 'placeholder': 'Phone...', 'type': 'text'}))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if Customer.objects.filter(phone=phone).exists():
            raise ValidationError("Phone Number exists, try another")
        if len(phone) != 11:
            raise ValidationError("Phone number must be eleven characters")
        try:
            dummy_phone = int(phone[1:])  # Sliced
            phone = dummy_phone
        except:
            raise ValidationError("Phone number not valid")
        if not isinstance(phone, int):
            raise ValidationError("Phone number not valid")
        return phone

    class Meta:
        model = Customer
        fields = ['phone']


class CreateUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username...'}))
    password1 = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Password...', 'type': 'password'}))
    password2 = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Repeat your password...', 'type': 'password'}))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email...', 'type': 'email'}))

    class Meta:
        model = User
        fields = ('username', 'email',  'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists, try another")
        return email
