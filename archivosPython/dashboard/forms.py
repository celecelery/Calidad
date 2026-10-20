from django import forms
from .models import *

class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = [
            'nombre',
            'fecha_inicio',
            'fecha_fin'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }
    

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'nombre',
            'descripcion',
            'integrantes',
            'lider',
            'periodo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'integrantes': forms.TextInput(attrs={'class': 'form-control'}),
            'lider': forms.TextInput(attrs={'class': 'form-control'}),
            'periodo':forms.TextInput(attrs={'class': 'form-control'})
        }
