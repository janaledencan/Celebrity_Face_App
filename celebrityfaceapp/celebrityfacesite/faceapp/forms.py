from django.forms import ModelForm, ValidationError
from django import forms
from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "age",
            "sex",
            "image",
        ]

        widgets = {
            "age": forms.Select(attrs={"class": "form-control"}),
            "sex": forms.Select(attrs={"class": "form-control"}),
            'image': forms.FileInput(attrs={
                'style': 'margin-left: 20px;'}),
        }
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
       

    def clean(self):
        errors = []

        if errors:
            raise ValidationError(errors)
        return self.cleaned_data


