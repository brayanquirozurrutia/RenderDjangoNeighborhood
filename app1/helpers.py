from django.core.mail import send_mail
import secrets
from django.utils import timezone
from .models import PasswordResetToken

from Neighborhood import settings

class Functions():
    def valida_entero(self, numero):
        """Valida si la entrada es un número entero.

        Args:
            numero (str): El número a validar.

        Returns:
            bool: True si es un número entero, False en caso contrario.
        """
        try:
            int(numero)
            return True
        except ValueError:
            return False

    def valida_rut(self, rut):
        """Valida un RUT chileno.

        Args:
            rut (str): El RUT a validar.

        Returns:
            bool: True si el RUT es válido, False si no cumple con los requisitos.
        """
        rut_sin_digito = rut[:-2]

        if self.valida_entero(self, rut_sin_digito) and 7 <= len(rut_sin_digito) <= 8:
            lista_rut_enteros = [int(digito) for digito in rut_sin_digito]
            lista_rut_enteros.reverse()

            ponderador = 2
            suma_producto = 0
            for digito in lista_rut_enteros:
                producto = ponderador * digito
                ponderador += 1
                suma_producto += producto
                if ponderador == 8:
                    ponderador = 2

            resto = suma_producto % 11
            diferencia = 11 - resto

            if diferencia == 11:
                digito_verificador = 0
            elif diferencia == 10:
                digito_verificador = 'k'
            else:
                digito_verificador = diferencia

            return str(digito_verificador) == (rut[-1])
        
        return False
    
    def notificar_alerta_por_correo(self, mensaje_de_alerta, nombre_de_usuario, latitud, longitud, correos):
        
        cuerpo_correo = f'{mensaje_de_alerta}\n\nTu contacto de emergencia {nombre_de_usuario} ha emitido una alerta en las coordenadas latitud: {latitud}, longitud: {longitud}\n\nVisita el siguiente link para acceder inmediatamente https://www.google.com/maps?q={latitud},{longitud}'
        
        send_mail(
            "Se ha emitido una alerta",
            cuerpo_correo,
            settings.EMAIL_HOST_USER,
            correos,
            fail_silently=False,
            )
    
    def enviar_enlace_reset_contraseña(self, usuario):
        token = secrets.token_urlsafe()
        fecha_expiracion = timezone.now() + timezone.timedelta(minutes=15)  # Expire en 15 mimutos
        PasswordResetToken.objects.update_or_create(
            usuario=usuario,
            defaults={'token': token, 'fecha_expiracion': fecha_expiracion}
        )

        # Ahora, envía el enlace por correo
        enlace = f'http://http://127.0.0.1:8000/restablecer_contraseña/{token}/'
        send_mail(
            'Restablecimiento de Contraseña',
            f'Por favor, haz clic en el siguiente enlace para restablecer tu contraseña: {enlace}',
            settings.EMAIL_HOST_USER,
            [usuario.correo_usuario],
            fail_silently=False,
        )