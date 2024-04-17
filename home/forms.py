from django import forms
from .models import hospital_name

class DeleteHospitalForm(forms.Form):
    selected_ids = forms.ModelMultipleChoiceField(queryset=hospital_name.objects.all(), widget=forms.CheckboxSelectMultiple)