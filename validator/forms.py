from django import forms
from django.core.validators import RegexValidator

class PESELForm(forms.Form):
    pesel = forms.CharField(
        label='PESEL',
        max_length=11,
        min_length=11,
        validators=[RegexValidator(r'^[0-9]{11}$', 'Enter exactly 11 digits')],
        widget=forms.TextInput(attrs={'placeholder': 'Enter 11 digits'})
    )
