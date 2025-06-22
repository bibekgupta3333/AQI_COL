"""
Django forms for the AQI prediction application
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserRegistrationForm(UserCreationForm):
    """
    Enhanced user registration form with additional validation
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username (3-150 characters)'
        }),
        help_text='Required. 3-150 characters. Letters, digits and @/./+/-/_ only.'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        help_text='Password must be at least 8 characters long.'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        help_text='Enter the same password as before, for verification.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class UserLoginForm(forms.Form):
    """
    User login form with validation
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class AQIPredictionForm(forms.Form):
    """
    Form for AQI prediction with comprehensive validation
    """
    # Temperature fields (in Celsius)
    T = forms.FloatField(
        label='Average Temperature (°C)',
        validators=[MinValueValidator(-50), MaxValueValidator(60)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 25.5',
            'step': '0.1',
            'min': '-50',
            'max': '60'
        }),
        help_text='Average temperature in Celsius (-50 to 60)'
    )
    
    TM = forms.FloatField(
        label='Maximum Temperature (°C)',
        validators=[MinValueValidator(-50), MaxValueValidator(60)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 30.0',
            'step': '0.1',
            'min': '-50',
            'max': '60'
        }),
        help_text='Maximum temperature in Celsius (-50 to 60)'
    )
    
    Tm = forms.FloatField(
        label='Minimum Temperature (°C)',
        validators=[MinValueValidator(-50), MaxValueValidator(60)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 20.0',
            'step': '0.1',
            'min': '-50',
            'max': '60'
        }),
        help_text='Minimum temperature in Celsius (-50 to 60)'
    )
    
    # Atmospheric pressure
    SLP = forms.FloatField(
        label='Sea Level Pressure (hPa)',
        validators=[MinValueValidator(900), MaxValueValidator(1100)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 1013.25',
            'step': '0.01',
            'min': '900',
            'max': '1100'
        }),
        help_text='Sea level pressure in hPa (900-1100)'
    )
    
    # Humidity
    H = forms.FloatField(
        label='Relative Humidity (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 65.0',
            'step': '0.1',
            'min': '0',
            'max': '100'
        }),
        help_text='Relative humidity as percentage (0-100)'
    )
    
    # Visibility
    VV = forms.FloatField(
        label='Visibility (km)',
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 10.0',
            'step': '0.1',
            'min': '0',
            'max': '50'
        }),
        help_text='Visibility in kilometers (0-50)'
    )
    
    # Wind speed
    V = forms.FloatField(
        label='Wind Speed (km/h)',
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 15.0',
            'step': '0.1',
            'min': '0',
            'max': '200'
        }),
        help_text='Wind speed in km/h (0-200)'
    )
    
    # Wind gust
    VM = forms.FloatField(
        label='Wind Gust (km/h)',
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 25.0',
            'step': '0.1',
            'min': '0',
            'max': '300'
        }),
        help_text='Wind gust speed in km/h (0-300)'
    )

    def clean(self):
        """
        Cross-field validation
        """
        cleaned_data = super().clean()
        
        # Temperature validation
        t_avg = cleaned_data.get('T')
        t_max = cleaned_data.get('TM')
        t_min = cleaned_data.get('Tm')
        
        if t_avg and t_max and t_min:
            if t_min > t_avg:
                raise forms.ValidationError(
                    "Minimum temperature cannot be higher than average temperature."
                )
            if t_avg > t_max:
                raise forms.ValidationError(
                    "Average temperature cannot be higher than maximum temperature."
                )
            if t_min > t_max:
                raise forms.ValidationError(
                    "Minimum temperature cannot be higher than maximum temperature."
                )
        
        # Wind validation
        wind_speed = cleaned_data.get('V')
        wind_gust = cleaned_data.get('VM')
        
        if wind_speed and wind_gust:
            if wind_speed > wind_gust:
                raise forms.ValidationError(
                    "Wind speed cannot be higher than wind gust speed."
                )
        
        return cleaned_data


class DataFilterForm(forms.Form):
    """
    Form for filtering historical data
    """
    YEAR_CHOICES = [
        ('', 'All Years'),
        ('2018', '2018'),
        ('2019', '2019'),
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
    ]
    
    year_filter = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit();'
        }),
        label='Filter by Year'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Start Date'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='End Date'
    )

    def clean(self):
        """
        Validate date range
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(
                    "Start date cannot be after end date."
                )
        
        return cleaned_data


class ContactForm(forms.Form):
    """
    Contact form for user feedback
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message'
        })
    ) 