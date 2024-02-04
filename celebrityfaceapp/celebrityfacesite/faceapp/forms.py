from django.forms import ModelForm, ValidationError
from django import forms
from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "age",
            "sex",
        ]

        widgets = {
            "age": forms.Select(attrs={"class": "form-control"}),
            "sex": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
       

    def clean(self):
        errors = []

        if errors:
            raise ValidationError(errors)
        return self.cleaned_data
