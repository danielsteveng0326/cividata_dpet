# forms.py
from django import forms
from .models import Peticion, Dependencia


class PeticionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Si el usuario es Jefe Jurídica (dependencia 111), mostrar campo dependencia
        if self.user and self.user.dependencia and self.user.dependencia.prefijo == '111':
            self.fields['dependencia'] = forms.ModelChoiceField(
                queryset=Dependencia.objects.filter(activa=True).order_by('nombre_oficina'),
                required=True,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Dependencia Responsable',
                help_text='Seleccione la dependencia que debe responder esta petición'
            )
        else:
            # Para otros usuarios, ocultar el campo (se asigna automáticamente)
            if 'dependencia' in self.fields:
                self.fields['dependencia'].required = False
                self.fields['dependencia'].widget = forms.HiddenInput()
    
    class Meta:
        model = Peticion
        fields = [
            'fecha_radicacion',
            'dependencia',
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


class MarcarRespondidoForm(forms.ModelForm):
    """Formulario para marcar una petición como respondida con archivos adjuntos"""
    
    class Meta:
        model = Peticion
        fields = ['archivo_respuesta_firmada', 'archivo_constancia_envio']
        widgets = {
            'archivo_respuesta_firmada': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True
            }),
            'archivo_constancia_envio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png',
                'required': True
            })
        }
        labels = {
            'archivo_respuesta_firmada': 'Respuesta Firmada',
            'archivo_constancia_envio': 'Constancia de Envío'
        }
    
    def clean_archivo_respuesta_firmada(self):
        archivo = self.cleaned_data.get('archivo_respuesta_firmada')
        if archivo:
            extensiones_validas = ['.pdf', '.doc', '.docx']
            if not any(archivo.name.lower().endswith(ext) for ext in extensiones_validas):
                raise forms.ValidationError('Solo se permiten archivos PDF, DOC o DOCX.')
            if archivo.size > 10 * 1024 * 1024:  # 10MB máximo
                raise forms.ValidationError('El archivo no puede ser mayor a 10MB.')
        return archivo
    
    def clean_archivo_constancia_envio(self):
        archivo = self.cleaned_data.get('archivo_constancia_envio')
        if archivo:
            extensiones_validas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if not any(archivo.name.lower().endswith(ext) for ext in extensiones_validas):
                raise forms.ValidationError('Solo se permiten archivos PDF, DOC, DOCX o imágenes.')
            if archivo.size > 10 * 1024 * 1024:  # 10MB máximo
                raise forms.ValidationError('El archivo no puede ser mayor a 10MB.')
        return archivo
