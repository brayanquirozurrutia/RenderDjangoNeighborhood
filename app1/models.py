from datetime import datetime
from django.db import models
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
from django.db.models.signals import post_save

# ---------------------------------------------- Modelos Nivel 1 ----------------------------------------------
class Usuario(models.Model):
    
    GENERO_CHOICES = (
        ('F', 'Femenino'),
        ('M', 'Masculino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decirlo'),
    )
    
    rut_usuario = models.CharField(max_length=100, primary_key=True)
    nombre_usuario = models.CharField(max_length=100)
    apellido_usuario = models.CharField(max_length=100)
    correo_usuario = models.EmailField(max_length=100)
    contrasenia_usuario = models.CharField(max_length=250)
    direccion_usuario = models.CharField(max_length=250)
    telefono_usuario = models.IntegerField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, default='N')
    foto_de_perfil = models.ImageField(upload_to='perfil/', null=True, blank=True)
    
    # Almacenamos la contraseña de manera segura usando hashing y salting
    def save(self, *args, **kwargs):
        
        self.nombre_usuario = self.nombre_usuario.strip().capitalize()
        self.apellido_usuario = self.apellido_usuario.strip().capitalize()
        self.direccion_usuario = self.direccion_usuario.strip().capitalize()

        self.contrasenia_usuario = make_password(self.contrasenia_usuario)
        super().save(*args, **kwargs)
        
class ContactoEmergencia(models.Model):
    rut_contacto_emergencia =  models.CharField(max_length=100, primary_key=True)
    es_usuario_app = models.BooleanField()
    
class Enfermedad(models.Model):
    id_enfermedad = models.IntegerField(primary_key=True)
    nombre_enfermedad = models.CharField()
    
class Medicamento(models.Model):
    id_medicamento = models.IntegerField(primary_key=True)
    nombre_medicamento = models.CharField()
    
class Alergia(models.Model):
    id_alergia = models.IntegerField(primary_key=True)
    nombre_alergia = models.CharField()

class Discapacidad(models.Model):
    id_discapacidad = models.IntegerField(primary_key=True)
    nombre_discapacidad = models.CharField()

# ---------------------------------------------- Modelos Nivel 2 ----------------------------------------------
class DetalleContactoEmergencia(models.Model):
    id = models.AutoField(primary_key=True)
    rut_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    rut_contacto_emergencia = models.ForeignKey("ContactoEmergencia", on_delete=models.CASCADE)
    fecha_adicion = models.DateField(max_length=100)

    class Meta:
        unique_together = ('rut_usuario', 'rut_contacto_emergencia')

class Evento(models.Model):
    id_evento =  models.AutoField(primary_key=True)
    hora_evento =  models.CharField(max_length=100)
    fecha_evento = models.DateField(max_length=100)
    ubicacion_evento = models.CharField(max_length=100)
    rut_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)

class Cuenta(models.Model):
    id_cuenta = models.AutoField(primary_key=True)
    fecha_creacion = models.DateField(default=datetime.now().strftime('%Y-%m-%d'))
    estado_cuenta = models.BooleanField(default=False)
    rut_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    
    @receiver(post_save, sender=Usuario)
    def create_user_account(sender, instance, created, **kwargs):
        if created:
            # Solo se ejecuta si se crea un nuevo usuario
            Cuenta.objects.create(rut_usuario=instance)

class MensajeDeAlerta(models.Model):
    id_mensaje_alerta = models.AutoField(primary_key=True)
    mensaje_alerta = models.CharField(max_length=100)
    rut_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    
class InformacionDeSalud(models.Model):
    id_info_salud = models.AutoField(primary_key=True)
    altura = models.IntegerField()
    peso = models.IntegerField()
    fecha_nacimiento = models.DateField()
    rut_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)

class PasswordResetToken(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    fecha_expiracion = models.DateTimeField()

class ActivateAccountToken(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    token_aat = models.CharField(max_length=255)
    fecha_expiracion_aat = models.DateTimeField()

# ---------------------------------------------- Modelos Nivel 3 ----------------------------------------------
class Sesion(models.Model):
    id_inicio_sesion = models.AutoField(primary_key=True)
    fecha_inicio_sesion = models.DateField(max_length=100)
    hora_inicio_sesion = models.CharField(max_length=100)
    ubicacion_inicio_sesion = models.CharField(max_length=100)
    id_cuenta = models.ForeignKey("Cuenta", on_delete=models.CASCADE)
    
class Marcador(models.Model):
    id_marcador = models.AutoField(primary_key=True)
    latitud = models.CharField(max_length=100)
    longitud = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField()
    rut_usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    mensade_de_alerta = models.ForeignKey("MensajeDeAlerta", on_delete=models.CASCADE)

class DetalleEnfermedad(models.Model):
    id_enfermedad = models.ForeignKey("Enfermedad", on_delete=models.CASCADE)
    id_info_salud = models.ForeignKey("InformacionDeSalud", on_delete=models.CASCADE)
    mostrar_enfermedad = models.BooleanField()
    
    class Meta:
        unique_together = ('id_enfermedad', 'id_info_salud')

class DetalleMedicamento(models.Model):
    id_medicamento = models.ForeignKey("Medicamento", on_delete=models.CASCADE)
    id_info_salud = models.ForeignKey("InformacionDeSalud", on_delete=models.CASCADE)
    mostrar_medicamento= models.BooleanField()
    
    class Meta:
        unique_together = ('id_medicamento', 'id_info_salud')

class DetalleAlergia(models.Model):
    id_alergia = models.ForeignKey("Alergia", on_delete=models.CASCADE)
    id_info_salud = models.ForeignKey("InformacionDeSalud", on_delete=models.CASCADE)
    mostrar_alergia = models.BooleanField()
    
    class Meta:
        unique_together = ('id_alergia', 'id_info_salud')
        
class DetalleDiscapacidad(models.Model):
    id_discapacidad = models.ForeignKey("Discapacidad", on_delete=models.CASCADE)
    id_info_salud = models.ForeignKey("InformacionDeSalud", on_delete=models.CASCADE)
    mostrar_discapacidad= models.BooleanField()
    
    class Meta:
        unique_together = ('id_discapacidad', 'id_info_salud')
    