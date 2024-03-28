from .models import Destinations, Verify
from django import forms
class DestForm(forms.ModelForm):
    class Meta:
        model=Destinations
        fields='__all__'

class VerForm(forms.ModelForm):
    class Meta:
        model=Verify
        fields='__all__'
