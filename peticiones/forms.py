# forms.py
from django import forms
from .models import Peticion


class PeticionForm(forms.ModelForm):
    class Meta:
        model = Peticion
        fields = [
            'fecha_radicacion',
            'peticionario_nombre', 
            'peticionario_id', 
            'peticionario_telefono',
            'peticionario_correo', 
            'peticionario_direccion',
            'archivo_pdf',
            'fuente'
        ]
        widgets = {
            'fecha_radicacion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'peticionario_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del peticionario (opcional)'
            }),
            'peticionario_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cédula o documento (opcional)'
            }),
            'peticionario_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto (opcional)'
            }),
            'peticionario_correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com (opcional)'
            }),
            'peticionario_direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa (opcional)'
            }),
            'archivo_pdf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'fuente': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'fecha_radicacion': 'Fecha y Hora de Radicación',
            'peticionario_nombre': 'Nombre del Peticionario',
            'peticionario_id': 'Documento de Identidad',
            'peticionario_telefono': 'Teléfono',
            'peticionario_correo': 'Correo Electrónico',
            'peticionario_direccion': 'Dirección',
            'archivo_pdf': 'Archivo PDF del Derecho de Petición',
            'fuente': 'Fuente de Recepción'
        }

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Solo se permiten archivos PDF.')
            if archivo.size > 10 * 1024 * 1024:  # 10MB máximo
                raise forms.ValidationError('El archivo no puede ser mayor a 10MB.')
        return archivo
