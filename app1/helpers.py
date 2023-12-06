from django.core.mail import send_mail
import secrets
from django.utils import timezone
from .models import PasswordResetToken, ActivateAccountToken
from math import sqrt
import utm

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
        """_summary_

        Args:
            mensaje_de_alerta (_type_): _description_
            nombre_de_usuario (_type_): _description_
            latitud (_type_): _description_
            longitud (_type_): _description_
            correos (_type_): _description_
        """
        
        cuerpo_correo = f'{mensaje_de_alerta}\n\nTu contacto de emergencia {nombre_de_usuario} ha emitido una alerta en las coordenadas latitud: {latitud}, longitud: {longitud}\n\nVisita el siguiente link para acceder inmediatamente https://www.google.com/maps?q={latitud},{longitud}'
        
        send_mail(
            "Se ha emitido una alerta",
            cuerpo_correo,
            settings.EMAIL_HOST_USER,
            correos,
            fail_silently=False,
            )
    
    def enviar_enlace_reset_contraseña(self, usuario):
        """Genera y envía un enlace al correo del usuario para cambiar su contraseña.

        Args:
            usuario (object): Objeto del modelo Usuario

        Details:
            Esta función genera un token único y una fecha de expiración asociada para cambiar la contrasela de la cuenta del usuario.
            El token y la fecha de expiración se almacenan en la base de datos usando el modelo PasswordResetToken.

        Note:
            Esta función no retorna ningún valor directamente, ya que actualiza la base de datos y envía el enlace por correo.
        """
        token = secrets.token_urlsafe()
        fecha_expiracion = timezone.now() + timezone.timedelta(minutes=15)  # Expire en 15 mimutos
        PasswordResetToken.objects.update_or_create(
            usuario=usuario,
            defaults={'token': token, 'fecha_expiracion': fecha_expiracion}
        )

        # Ahora, envía el enlace por correo
        enlace = f'http://127.0.0.1:8000/reset_password/{token}/'
        send_mail(
            'Restablecimiento de Contraseña',
            f'Por favor, haz clic en el siguiente enlace para restablecer tu contraseña: {enlace}\n\nEste enlace tiene una duración de 15 minutos desde la recepción de este correo',
            settings.EMAIL_HOST_USER,
            [usuario.correo_usuario],
            fail_silently=False,
        )
    
    def enviar_enlace_confirmar_cuenta(self, usuario):
        """Genera y envía un enlace al correo del usuario para confirmar la creación de su cuenta en Neighborhood.

        Args:
            usuario (object): Objeto del modelo Usuario

        Details:
            Esta función genera un token único y una fecha de expiración asociada para activar la cuenta del usuario.
            El token y la fecha de expiración se almacenan en la base de datos usando el modelo ActivateAccountToken.

        Note:
            Esta función no retorna ningún valor directamente, ya que actualiza la base de datos y envía el enlace por correo.
        """
        token_aat = secrets.token_urlsafe()
        fecha_expiracion_aat = timezone.now() + timezone.timedelta(minutes=15)
        ActivateAccountToken.objects.update_or_create(
            usuario=usuario,
            defaults={'token_aat': token_aat, 'fecha_expiracion_aat': fecha_expiracion_aat}
        )

        enlace = f'http://127.0.0.1:8000/activate_account/{token_aat}/'
        send_mail(
            'Activar cuenta',
            f'Hola {usuario.nombre_usuario}, por favor, haz clic en el siguiente enlace para activar tu cuenta: {enlace}\n\nEste enlace tiene una duración de 15 minutos desde la recepción de este correo',
            settings.EMAIL_HOST_USER,
            [usuario.correo_usuario],
            fail_silently=False,
        )
    
    def cards_content(self):
        """Crea el contenido de los card para usar en el index.html.

        Returns:
            tuple: Listado con el contenido de los cards en dos secciones distintas del index.html.
                El primer elemento de la tupla contiene cards para una sección.
                El segundo elemento de la tupla contiene cards_carousel para otra sección.
        """
        
        cards = [
            {
                'title': 'Parque Bicentenario',
                'src': 'images/parque_bicentenario.webp',
                'alt': 'Imagen parque bicentenario'
            },
            {
                'title': 'Parque Metropolitano',
                'src': 'images/parque_metropolitano.webp',
                'alt': 'Imagen parque Metropolitano'
            },
            {
                'title': 'Parque Araucano',
                'src': "images/parque_araucano.webp",
                'alt': 'Imagen parque Araucano'
            },
            ]
        
        cards_carousel = [
            {
                "title": "Las Condes", 
                "src": "images/las_condes.webp",
                "alt": "Imagen Las Condes"
            },
            {
                "title": "Santiago Centro",
                "src": "images/santiago_centro.webp",
                "alt": "Imagen Santiago Centro"
            },
            {
                "title": "Vitacura",
                "src": "images/vitacura.webp",
                "alt": "Imagen Vitacura"
            },
            {
                "title": "Lo Barnechea",
                "src": "images/lo_barnechea.webp",
                "alt": "Imagen Lo Barnechea"
            },
            {
                "title": "Providencia",
                "src": "images/providencia.webp",
                "alt": "Imagen Providencia"
            },
            {
                "title": "Ñuñoa",
                "src": "images/ñuñoa.webp",
                "alt": "Imagen Ñuñoa"
            },
            {
                "title": "Huechuraba",
                "src": "images/huechuraba.webp",
                "alt": "Imagen Huechuraba"
            },
            {
                "title": "Peñalolen",
                "src": "images/peñalolen.webp",
                "alt": "Imagen Peñalolen"
            },
            ]
        
        for i, card in enumerate(cards, start=1):
            card['data_bs_target'] = f'modal_{i}'
            card['content'] = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Minus, molestiae doloribus. Esse quod perferendis mollitia accusamus, impedit expedita hic qui sit, animi eius laudantium totam aut sapiente provident. Omnis, officia'
    
        for i, card in enumerate(cards_carousel, start=1):
            card['data_bs_target'] = f'modal_carousel_{i}'
            card['content'] = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Minus, molestiae doloribus. Esse quod perferendis mollitia accusamus, impedit expedita hic qui sit, animi eius laudantium totam aut sapiente provident. Omnis, officia'
        
        return cards, cards_carousel
    
    def zona_alertas(self, latitud_centro, longitud_centro, latitud_alerta, longitud_alerta):
        """Calcula la distancia entre la ubicación del usuario que inicia sesión y la ubicación de las alertas activas emitidas dentro de Neighborhood

        Args:
            latitud_centro (str): Latitud del usuario que inicia sesión
            longitud_centro (str): Longitud del usuario que inicia sesión
            latitud_alerta (str): Latitud de la alerta cercana activa
            longitud_alerta (str): Longitud de la alerta cercana activa
        
        Details:
            Esta función transforma las coordenadas geográficas en coordenadas UTM para obtener distancias en metros.

        Returns:
            float: Distancia entre el usuario que inicia sesión y el marcador activo dentro del mapa
        """
        utm_centro = utm.from_latlon(float(latitud_centro), float(longitud_centro))
        utm_alerta = utm.from_latlon(float(latitud_alerta), float(longitud_alerta))
        
        radio = sqrt((utm_alerta[0] - utm_centro[0])**2 + (utm_alerta[1] - utm_centro[1])**2)
        
        return radio
        
        