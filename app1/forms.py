from typing import Any
from django import forms
from django.contrib.auth.hashers import check_password

from app1.helpers import Functions

from app1.models import Usuario

class LogInForm(forms.Form):
    rut_usuario = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'input_',
        'placeholder': 'RUT Usuario',
        'id': 'rut_usuario',
        'name': 'rut_usuario',
        'required': 'required',
        }))
    
    contrasenia = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input_',
        'placeholder': 'Contraseña',
        'id': 'contrasenia',
        'name': 'contrasenia',
        'required': 'required',
    }))
    
    def clean(self):
        cleaned_data = super().clean()
        
        rut = cleaned_data.get('rut_usuario').strip()
        contrasenia = cleaned_data.get('contrasenia')
        
        rut_valido = Functions.valida_rut(Functions, rut)
        rut_existe = Usuario.objects.filter(rut_usuario=rut).exists()
        
        if not rut_valido:
            self.add_error('rut_usuario', "RUT no válido, considere formato 12345678-1")
        elif not rut_existe:
            self.add_error('rut_usuario', "El RUT ingresado no existe")
        else:
            usuario = Usuario.objects.get(rut_usuario=rut)
            contrasenia_correcta = check_password(contrasenia, usuario.contrasenia_usuario)
            if not contrasenia_correcta:
                self.add_error('contrasenia', 'Contraseña incorrecta')

class CreateAccountForm(forms.ModelForm):
    
    reingrese_correo = forms.EmailField(label='Reingrese correo', label_suffix= 'floatingInput', widget=forms.EmailInput(attrs={
        'placeholder': 'correo@mail.cl'
        }))
    
    reingrese_contrasenia = forms.CharField(label='Reingrese contraseña', widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese su contraseña'
        }))

    class Meta:
        model = Usuario
        fields = [
            'rut_usuario', 'nombre_usuario', 'apellido_usuario', 'correo_usuario', 'reingrese_correo', 'direccion_usuario', 'telefono_usuario', 'genero', 'foto_de_perfil', 'contrasenia_usuario', 'reingrese_contrasenia'
            ]
        
        contrasenia_usuario = forms.CharField(widget=forms.PasswordInput())
        
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Ingrese su nombre'}),
            'apellido_usuario': forms.TextInput(attrs={'placeholder': 'Ingrese su apellido'}),
            'rut_usuario': forms.TextInput(attrs={'placeholder': '12345678-1'}),
            'correo_usuario': forms.EmailInput(attrs={'placeholder': 'correo@mail.cl'}),
            'reingrese_correo': forms.EmailInput(attrs={'placeholder': 'correo@mail.cl'}),
            'direccion_usuario': forms.TextInput(attrs={'placeholder': 'Ingrese su dirección'}),
            'telefono_usuario': forms.NumberInput(attrs={'placeholder': '987654321'}),
            'contrasenia_usuario': forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}),
            'reingrese_contrasenia': forms.PasswordInput(attrs={'placeholder': 'Reingrese su contraseña'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'foto_de_perfil': forms.FileInput(attrs={'name': 'foto_de_perfil'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases a las etiquetas (labels)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control input_ca'
            field.label_classes = 'form-label'
        
    def clean(self):
        cleaned_data = super().clean()
        
        rut = cleaned_data.get('rut_usuario').strip()
        correo = cleaned_data.get('correo_usuario').strip()
        correo_2 = cleaned_data.get('reingrese_correo').strip()
        telefono = str(cleaned_data.get('telefono_usuario')).strip()
        contrasenia = cleaned_data.get('contrasenia_usuario').strip()
        contrasenia_2 = cleaned_data.get('reingrese_contrasenia').strip()
        
        usuario_existente = Usuario.objects.filter(rut_usuario=rut).first()
        rut_valido = Functions.valida_rut(Functions, rut)
        
        if usuario_existente is not None:
            self.add_error('rut_usuario', 'El rut ya está registrado')
        elif not rut_valido:
            self.add_error('rut_usuario', 'RUT no válido, considere formato 12345678-1')
        elif correo != correo_2:
            self.add_error('correo_usuario', 'Los correos no coinciden')
        elif len(telefono) != 9:
            self.add_error('telefono_usuario', 'Teléfono no válido, considere formato 987654321')
        elif contrasenia != contrasenia_2:
            self.add_error('contrasenia_usuario', 'Las contraseñas no coinciden')

class ChangePasswordForm(forms.Form):
    rut_usuario = forms.CharField(label='RUT', max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '12345678-5',
        'id': 'rut_usuario',
        'name': 'rut_usuario',
        'required': 'required',
        }))
    
    def clean(self):
        cleaned_data = super().clean()
        
        rut = cleaned_data.get('rut_usuario').strip()

        rut_valido = Functions.valida_rut(Functions, rut)
        usuario_existente = Usuario.objects.filter(rut_usuario=rut).first()
        
        if not rut_valido:
            self.add_error('rut_usuario', 'RUT no válido, considere formato 12345678-1')
        elif usuario_existente is None:
            self.add_error('rut_usuario', 'El RUT no está registrado')
        
class ReestablecerContraseniaForm(forms.Form):
    nueva_contrasenia = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nueva contraseña',
        'id': 'nueva_contraseña',
        'required': 'required',
    }))
    reingrese_contrasenia = forms.CharField(label='Re ingrese contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Reingrese contraseña',
        'id': 'reingrese_contraseña',
        'required': 'required',
    }))
    
    def clean(self):
        cleaned_data = super().clean()
        
        contrasenia = cleaned_data.get('nueva_contrasenia').strip()
        contrasenia_2 = cleaned_data.get('reingrese_contrasenia').strip()
        
        if contrasenia != contrasenia_2:
            self.add_error('nueva_contrasenia', 'Las contraseñas no coinciden')

class NewContactEmergencyForm(forms.Form):
    rut_contacto_emergencia = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'rut_contacto_emergencia',
        'name': 'rut_contacto_emergencia',
        'required': True,
        'placeholder': 'rut_contacto_emergencia',
        }))

    def __init__(self, *args, **kwargs):
        self.rut_usuario = kwargs.pop('rut_usuario', None)
        super(NewContactEmergencyForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        rut_contacto_emergencia = cleaned_data.get('rut_contacto_emergencia').strip()
        rut_valido = Functions.valida_rut(Functions, rut_contacto_emergencia)
        
        if not rut_valido:
            self.add_error('rut_contacto_emergencia', 'RUT no válido, considere formato 12345678-1')
        elif rut_contacto_emergencia == self.rut_usuario:
            self.add_error('rut_contacto_emergencia', '¿Estás tratando de añadirte como amigo...?')

class EditAlertMessage(forms.Form):
    mensaje_de_alerta = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'mensaje_de_alerta',
            'name': 'mensaje_de_alerta',
            'required': True,
            'placeholder': 'mensaje_de_alerta',
        })
    )
    
class SaludForm(forms.Form):
    altura = forms.FloatField(label='Altura (cm)')
    peso = forms.FloatField(label='Peso (Kg)', widget=forms.NumberInput(attrs={'step': 0.1}))
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases a las etiquetas (labels)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.label_classes = 'form-label'
            field.widget.attrs['placeholder'] = field.label

class AlergiasForm(forms.Form):
    alergia = forms.ChoiceField(choices=[
        ('1', 'Perros'), ('2', 'Gatos'), ('3', 'Polvo'),
        ('4', 'Maní'), ('5', 'Almendras'), ('6', 'Abejas')
        ], widget=forms.Select(attrs={'class': 'form-select'}))
    mostrar_alergia = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases a las etiquetas (labels)
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = field.label

class DiscapacidadesForm(forms.Form):
    discapacidad = forms.ChoiceField(choices=[
        ('1', 'Visual'), ('2', 'Auditiva'), ('3', 'Cognitiva'),
        ('4', 'Sensorial'), ('5', 'Intelectual'), ('6', 'Física')
        ], widget=forms.Select(attrs={'class': 'form-select'}))
    mostrar_discapacidad = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases a las etiquetas (labels)
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = field.label

class MedicamentosForm(forms.Form):
    medicamento = forms.ChoiceField(choices=[
        ('1', 'Benazepril'), ('2', 'Captopril'), ('3', 'Amitriptilina'),
        ('4', 'Amoxapina'), ('5', 'Escitalopram '), ('6', 'Duloxetina')
        ], widget=forms.Select(attrs={'class': 'form-select'}))
    mostrar_medicamento = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases a las etiquetas (labels)
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = field.label

class EnfermedadesForm(forms.Form):
    enfermedad = forms.ChoiceField(choices=[
        ('1', 'Hipertensión'), ('2', 'Hipotensión'), ('3', 'Agorafobia'),
        ('4', 'Diabetes'), ('5', 'Anemia'), ('6', 'Asma')
        ], widget=forms.Select(attrs={'class': 'form-select'}))
    mostrar_enfermedad = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases a las etiquetas (labels)
        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = field.label