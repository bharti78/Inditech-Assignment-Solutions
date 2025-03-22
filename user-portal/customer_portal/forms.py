from django import forms
from .models import Customer
from datetime import date

class CustomerForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Format: YYYY-MM-DD'
    )
    
    class Meta:
        model = Customer
        fields = ['first_name', 'middle_name', 'last_name', 'gender', 'email', 'phone', 'date_of_birth', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your middle name (optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'gender': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your full address', 'rows': 3}),
        }
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        today = date.today()
        
        if dob and dob > today:
            raise forms.ValidationError("Date of birth cannot be in the future")
        
        return dob
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        # Remove any non-digit characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        if len(phone_digits) < 10:
            raise forms.ValidationError("Phone number must have at least 10 digits")
        
        return phone
