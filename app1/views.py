from datetime import datetime, time, timedelta
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import folium
from app1 import forms
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from app1.models import ContactoEmergencia, Cuenta, DetalleContactoEmergencia, Evento, MensajeDeAlerta, PasswordResetToken, Sesion, Usuario, Marcador, DetalleEnfermedad, DetalleAlergia, DetalleDiscapacidad, DetalleMedicamento, InformacionDeSalud, Enfermedad, Medicamento, Discapacidad, Alergia, ActivateAccountToken

from app1.helpers import Functions

from app1.utils import get_usuario_by_rut, get_medical_record_status, get_medical_record_details

def indexTemplate(request):
    request.session['estado'] = False
    
    cards, cards_carousel = Functions.cards_content(Functions)
        
    data = {
        'cards': cards,
        'cards_carousel': cards_carousel,
    }
    
    return render(request, 'index.html', data)

def loginTemplate(request):
    form = forms.LogInForm()

    if request.method == 'POST':
        form = forms.LogInForm(request.POST)
        if form.is_valid():
            rut = request.POST.get('rut_usuario')
            contrasenia = request.POST.get('contrasenia')
            usuario = get_usuario_by_rut(rut)
            contrasenia_correcta = check_password(contrasenia, usuario.contrasenia_usuario)
            
            if contrasenia_correcta:
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                
                coordenadas_str = f'{latitude},{longitude}'
                sesion = Sesion(
                    fecha_inicio_sesion=datetime.now().strftime('%Y-%m-%d'),
                    hora_inicio_sesion=datetime.now().strftime('%H:%M:%S'),
                    ubicacion_inicio_sesion=coordenadas_str,
                    id_cuenta=Cuenta.objects.get(rut_usuario=rut)
                )
                sesion.save()
                
                # Enviamos datos de sesión
                request.session['estado'] = True
                request.session['rut_usuario'] = rut
                request.session['latitud'] = str(latitude)
                request.session['longitud'] = str(longitude)

                return redirect('home')
            else:
                return redirect('index')

    data = {
        'Form': form,
        'error': None,
    }

    return render(request, 'login.html', data)

def createAccountTemplate(request):
    form = forms.CreateAccountForm()
    
    data = {
            'Form': form,
            'error': None,
            }
    
    if request.method == 'POST':
        form = forms.CreateAccountForm(request.POST)
        if form.is_valid():
            try:
                my_image = request.FILES.get('foto_de_perfil')
                storage_location = os.path.join(settings.MEDIA_ROOT, 'perfil')
                fs = FileSystemStorage(location=storage_location)
                
                if my_image:
                    filename = fs.save(my_image.name, my_image)
                    form.instance.foto_de_perfil = 'perfil/' + filename
                else:
                    form.instance.foto_de_perfil = 'perfil/default.png'
                    
                form.save()
                
                # Obtenemos el RUT
                rut = request.POST.get('rut_usuario')
                # Buscamos al objeto usuario correspondiente al rut
                usuario = get_usuario_by_rut(rut)
                # Creamos el mensaje de alerta por defecto
                MensajeDeAlerta(mensaje_alerta='¡He sufrido un accidente!',
                                rut_usuario = usuario
                                ).save()
                
                Functions.enviar_enlace_confirmar_cuenta(Functions, usuario)
                
                return render (request, 'account_created.html')

            except Exception as e:
                print(e)
        else:
            data = {
                'Form': form,
                'error': 'Formulario no válido, verifique los campos',
            }
    else:
        form = forms.CreateAccountForm()
        data = {
            'Form': form,
            'error': 'Método distinto a POST'
        }
    
    return render(request, 'create-account.html', data)

def activar_cuenta(request, token):
    try:
        token_obj = get_object_or_404(ActivateAccountToken, token_aat=token)
    except:
        return render(request, 'expired_token_activate_account.html')
    
    if timezone.now() > token_obj.fecha_expiracion_aat:
        return render(request, 'expired_token.html')
    
    else:
        Cuenta.objects.get(rut_usuario=token_obj.usuario).estado_cuenta = True
        token_obj.delete()

    return render(request, 'activate_account.html')

def changePasswordTemplate(request):
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            rut = request.POST.get('rut_usuario')
            usuario = get_usuario_by_rut(rut)
            Functions.enviar_enlace_reset_contraseña(Functions, usuario)
            
            return redirect('index')
            
        else:
            data = {
                'Form': form,
                'error': 'Formulario no válido, verifique los campos'
            }
            return render(request, 'change-password.html', data)
    else:
        form = forms.ChangePasswordForm()
    
    data = {
        'Form': form,
        'error': None,
    }
    
    return render(request, 'change-password.html', data)

def restablecer_contraseña(request, token):
    try:
        token_obj = get_object_or_404(PasswordResetToken, token=token)
    except:
        return render(request, 'expired_token.html')
    error = None
    
    if timezone.now() > token_obj.fecha_expiracion:
        return render(request, 'expired_token.html')
    
    else:
        form = forms.ReestablecerContraseniaForm()
        if request.method == 'POST':
            form = forms.ReestablecerContraseniaForm(request.POST)
            if form.is_valid():
                usuario = token_obj.usuario
                nueva_contrasenia = request.POST.get('nueva_contrasenia')
                if check_password(nueva_contrasenia, usuario.contrasenia_usuario):
                    error = 'La nueva contraseña no puede ser igual a la actual'
                else:
                    usuario.contrasenia_usuario = nueva_contrasenia
                    usuario.save()
                    token_obj.delete()
                    return redirect('index')
                # redireccionar a una ´´agina simple que indica que la contraseña fue cambiada
    data = {
        'Form': form,
        'error': error,
    }

    return render(request, 'reset_password.html', data)


def homeTemplate(request):
    # Verificamos si hay una sesión activa
    
    # ------------------verificar que la cuenta esté activa--------------
    estado = request.session.get('estado', False)
    if estado:
        error = None; alerta_reiterada = None
        
        # Rescatamos los datos de quién inicio sesión
        rut_usuario = request.session.get('rut_usuario', None)
        latitud = request.session.get('latitud', None)
        longitud = request.session.get('longitud', None)
        
        # Obtenemos al usuario que inició sesión
        usuario = get_usuario_by_rut(rut_usuario)
        
        # Buscamos las sesiones del usuario que inicío sesión
        sesiones = Sesion.objects.filter(id_cuenta=Cuenta.objects.get(rut_usuario = rut_usuario)).order_by('-id_inicio_sesion')
        
        # Obtenemos la última vez en línea
        if len(sesiones) > 1:
            sesion_anterior = sesiones[1]
        else:
            sesion_anterior = sesiones[0]
            
        # Obtenemos datos relevantes
        nombre_usuario = usuario.nombre_usuario
        apellido_usuario = usuario.apellido_usuario
        fecha_inicio_sesion = sesion_anterior.fecha_inicio_sesion
        hora_inicio_sesion = sesion_anterior.hora_inicio_sesion
        foto_de_perfil = usuario.foto_de_perfil.url
        genero = usuario.genero
        
        # Definimos saludo
        if genero == 'F':
            saludo = 'Bienvenida'
        elif genero == 'M':
            saludo = 'Bienvenido'
        else:
            saludo = 'Hola'
        
        # Rescatamos las alertas activas para mostrarlas en el mapa
        alertas_activas = Marcador.objects.filter(fecha_hora__lte= datetime.now(),
                                                  fecha_hora__gt=(datetime.now()-timedelta(hours=2))
                                                  )
        
        # Crea un mapa centrado en una ubicación específica (por ejemplo, latitud y longitud)
        try:
            mapa = folium.Map(location=[latitud, longitud], zoom_start=16)
            
            # Punto ubicación usuario
            folium.Circle(
                location=[latitud, longitud],
                radius=2,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.2,
            ).add_to(mapa)

            # Radio de alertas
            folium.Circle(
                location=[latitud, longitud],
                radius=300,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.1,
            ).add_to(mapa)

            for marcador in alertas_activas:
                diccionario_ficha_medica = get_medical_record_details(marcador.__dict__['rut_usuario_id'])
                if diccionario_ficha_medica is not None:
                    contenido_popup = '''
                    <div class="container-fluid shadow rounded-4 my-2 py-2">
                        <div class="border rounded-4 px-4 mb-2">
                            <h3 class="fw-bold">{nombre} {apellido}</h3>
                        </div>
                        <div class="border rounded-4 px-4 mb-2">
                            <h5 class="text-center">{mensaje}</h5>
                        </div>
                        <div class="border rounded-4 px-4 py-1">
                        <h4 class="text-center fw-bold">Detalles</h4>
                            <ul class="list-unstyled">
                                {items}
                            </ul>
                        </div>
                    </div>'''.format(
                        nombre=marcador.rut_usuario.nombre_usuario,
                        apellido=marcador.rut_usuario.apellido_usuario,
                        mensaje=marcador.mensade_de_alerta.mensaje_alerta,
                        items='\n'.join([f"<li><strong>{key}:</strong> {value}</li>" for key, value in diccionario_ficha_medica.items() if value is not None]))
                else:
                    contenido_popup = '''
                    <div class="container-fluid shadow rounded-4 my-2 py-2">
                        <div class="border rounded-4 px-4 mb-2">
                            <h3 class="fw-bold">{nombre} {apellido}</h3>
                        </div>
                        <div class="border rounded-4 px-4 mb-2">
                            <h5 class="text-center">{mensaje}</h5>
                        </div>
                    </div>'''.format(
                        nombre=marcador.rut_usuario.nombre_usuario,
                        apellido=marcador.rut_usuario.apellido_usuario,
                        mensaje=marcador.mensade_de_alerta.mensaje_alerta,
                        )
                
                nuevo_marcador = folium.Marker(
                    location=[marcador.latitud, marcador.longitud],
                    popup=folium.Popup(contenido_popup, max_width=400),
                )
                
                nuevo_marcador.add_to(mapa)
            
            mapa_html = mapa._repr_html_()
            
        except Exception as e:
            print(f"Error al generar mapa: {e}")
            error = 'Error al generar mapa'
        
        
        # Validamos si se ha emitido una alerta
        if request.method == 'POST' and 'agregar_evento' in request.POST:
            # Buscamos la última alerta emitida por el usuario
            ultimo_evento = (Evento.objects.filter(rut_usuario=usuario).order_by('-id_evento').values_list('fecha_evento', 'hora_evento').first())
            # Verificamos si es su primera alerta
            if ultimo_evento != None:
                # Pasamos los datos a tipo datetime
                hora_ultimo_evento = [int(valor) for valor in ultimo_evento[1].split(':')]
                date_ultimo_evento = datetime.combine(ultimo_evento[0], time(hora_ultimo_evento[0], hora_ultimo_evento[1], hora_ultimo_evento[2]))
                # Calculamos la cantidad de segundos transcurridos entre la última alerta emitida y la siguiente
                delta_segundos = (datetime.now() - date_ultimo_evento).total_seconds()
            else:
                delta_segundos = 301
            # Verificamos si se puede emitir la alerta
            if(delta_segundos <= 300):
                alerta_reiterada = 'Debe esperar al menos 5 minutos para emitir la siguiente alerta'
            else:
                Evento(
                    hora_evento=datetime.now().strftime('%H:%M:%S'),
                    fecha_evento=datetime.now().strftime('%Y-%m-%d'),
                    ubicacion_evento=f'{latitud},{longitud}',
                    rut_usuario=usuario
                ).save()
                
                # Buscamos el mensaje de alerta
                mensaje_de_alerta = MensajeDeAlerta.objects.filter(rut_usuario=usuario).values_list('mensaje_alerta')[0][0]
                # Buscamos objeto MensajeDealerta asociado al rut_usuario
                mensaje_alerta_ = MensajeDeAlerta.objects.get(rut_usuario=usuario)
                
                # Almacenamos el marcador en la BBDD
                Marcador(latitud=latitud, longitud=longitud, fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rut_usuario=usuario, mensade_de_alerta=mensaje_alerta_).save()
                
                # Rescatamos listado de correos contactos de emergencia
                lista_rut_contactos_emergencia = DetalleContactoEmergencia.objects.filter(rut_usuario=rut_usuario).values_list('rut_contacto_emergencia', flat=True)
                
                correos_contactos_emergencia = Usuario.objects.filter(rut_usuario__in=lista_rut_contactos_emergencia).values('correo_usuario').values_list('correo_usuario')
                correos_contactos_emergencia = list(correos_contactos_emergencia)
                
                # Pasamos los correos a listado
                lista_correos = []
                
                for valor in correos_contactos_emergencia:
                    for sub_valor in valor:
                        lista_correos.append(sub_valor)
                try:
                    Functions.notificar_alerta_por_correo(Functions, mensaje_de_alerta, nombre_usuario, latitud, longitud, lista_correos)
                except Exception as e:
                    print(e)
                
                return redirect('home')
        
        data = {
            'rut_usuario': rut_usuario,
            'nombre_usuario': nombre_usuario,
            'apellido_usuario': apellido_usuario,
            'fecha_inicio_sesion': fecha_inicio_sesion,
            'hora_inicio_sesion': hora_inicio_sesion,
            'foto_de_perfil': foto_de_perfil,
            'latitud': latitud,
            'longitud': longitud,
            'mapa_html': mapa_html,
            'saludo': saludo,
            'error': error,
            'alerta_reiterada': alerta_reiterada,
        }
        
        return render(request, 'home.html', data)
    else:
        return redirect('login')

def friendsTemplate(request):
    estado = request.session.get('estado', False)
    if estado:
        detalle_contactos_emergencia = None

        # Rescatamos datos de inicio de sesión
        rut_usuario = request.session.get('rut_usuario', None)
        
        lista_rut_contactos_emergencia  = DetalleContactoEmergencia.objects.filter(rut_usuario=rut_usuario).values_list('rut_contacto_emergencia', flat=True)
        
        cantidad_de_contactos = len(lista_rut_contactos_emergencia)
        
        if cantidad_de_contactos > 0:
            usuarios_contacto_emergencia = Usuario.objects.filter(rut_usuario__in=lista_rut_contactos_emergencia).values('foto_de_perfil','nombre_usuario', 'apellido_usuario','rut_usuario').values_list('foto_de_perfil', 'nombre_usuario', 'apellido_usuario','rut_usuario')
            
            detalle_contactos_emergencia = []
            
            i = 0
            for usuario in usuarios_contacto_emergencia:
                url_foto = settings.MEDIA_URL + usuario[0]
                detalle_contactos_emergencia.append(list(usuario))
                detalle_contactos_emergencia[i][0] = url_foto
                i += 1
            
        # Validamos si se ha seleccionado un contacto de emergencia
        if request.method == 'POST' and 'editar_amigo' in request.POST:
            # Rescatamos el rut del contacto de emergencia seleccionado
            rut_contacto_emergencia = request.POST.get('editar_amigo')
            
            # Enviamos datos relevantes
            # request.session['rut_usuario'] = rut_usuario
            request.session['rut_contacto_emergencia'] = rut_contacto_emergencia
            
            return redirect('edit_friend')
        
        data = {
            'rut_usuario': rut_usuario,
            'cantidad_de_contactos': cantidad_de_contactos,
            'detalle_contactos_emergencia': detalle_contactos_emergencia,
        }
        
        return render(request, 'friends.html', data)
    else:
        return redirect('login')

def add_new_friend_template(request):
    estado = request.session.get('estado', False)
    error = None
    if estado:
        # Rescatamos datos de inicio de sesión
        rut_usuario = request.session.get('rut_usuario', None)
        
        form = forms.NewContactEmergencyForm()
        if request.method == 'POST':
            form = forms.NewContactEmergencyForm(request.POST, rut_usuario = rut_usuario)
            if form.is_valid():
                # Obtenemos el rut del contacto a añadir
                rut_contacto_emergencia = request.POST.get('rut_contacto_emergencia')
                
                posee_cuenta = Usuario.objects.filter(rut_usuario=rut_contacto_emergencia).exists()
                if(posee_cuenta):
                    nuevo_contacto = ContactoEmergencia(
                        rut_contacto_emergencia=rut_contacto_emergencia,
                        es_usuario_app=posee_cuenta
                    )
                    nuevo_contacto.save()
                    
                    ContactoEmergencia(
                        rut_contacto_emergencia=rut_usuario,
                        es_usuario_app=posee_cuenta
                    ).save()
                    
                    # rut_usuario añade a rut_contacto_emergencia
                    DetalleContactoEmergencia(
                        rut_usuario=Usuario.objects.get(rut_usuario=rut_usuario),
                        rut_contacto_emergencia=ContactoEmergencia.objects.get(rut_contacto_emergencia=rut_contacto_emergencia),
                        fecha_adicion=datetime.now().strftime('%Y-%m-%d')
                    ).save()
                    
                    # rut_contacto_emergencia añade a rut_usuario
                    DetalleContactoEmergencia(
                        rut_usuario=Usuario.objects.get(rut_usuario=rut_contacto_emergencia),
                        rut_contacto_emergencia=ContactoEmergencia.objects.get(rut_contacto_emergencia=rut_usuario),
                        fecha_adicion=datetime.now().strftime('%Y-%m-%d')
                    ).save()
                    
                    return redirect('home')
                else:
                    error = 'Usuario no registrado, invítalo a unirse mediante el siguiente link: http://127.0.0.1:8000/create-account/'
        
        data = {
            'Form': form,
            'rut_usuario': rut_usuario,
            'error': error,
        }
        
        return render(request, 'add-new-contact.html', data)
    else:
        return redirect('login')

def edit_friend(request):
    estado = request.session.get('estado', False)
    if estado:
        # Rescatamos los valores pasados
        rut_usuario = request.session.get('rut_usuario', None)
        rut_contacto_emergencia = request.session.get('rut_contacto_emergencia', None)
        
        usuario = get_usuario_by_rut(rut_contacto_emergencia)
        
        fecha_adicion = DetalleContactoEmergencia.objects.filter(rut_usuario=rut_usuario, rut_contacto_emergencia=rut_contacto_emergencia).values('fecha_adicion')
        
        fecha_adicion = fecha_adicion[0]['fecha_adicion']
        
        url_foto = usuario.foto_de_perfil.url
        nombre = usuario.nombre_usuario
        apellido = usuario.apellido_usuario
        telefono = usuario.telefono_usuario
        correo = usuario.correo_usuario
        
        # Verificamos que se haya eliminado un contacto
        if request.method == 'POST' and 'eliminar_contacto' in request.POST:
            # Eliminamos el registro de DetalleContactoEmergencia
            DetalleContactoEmergencia.objects.filter(rut_usuario=rut_usuario, rut_contacto_emergencia=rut_contacto_emergencia).delete()
            DetalleContactoEmergencia.objects.filter(rut_usuario=rut_contacto_emergencia, rut_contacto_emergencia=rut_usuario).delete()
            
            # Verificamos si el contacto de emergencia no está aádido por nadie más
            resultado = DetalleContactoEmergencia.objects.filter(rut_contacto_emergencia=rut_contacto_emergencia).count()
            
            # Si ya no es contacto de emergencia de nadie más, se elimina de la tabla ContactoEmergencia
            if resultado == 0:
                ContactoEmergencia.objects.filter(rut_contacto_emergencia=rut_contacto_emergencia).delete()
            
            return redirect('friends')
            
        data = {
            'rut_usuario': rut_usuario,
            'rut_contacto_emergencia': rut_contacto_emergencia,
            'url_foto': url_foto,
            'nombre': nombre,
            'apellido': apellido,
            'telefono': telefono,
            'correo': correo,
            'fecha_adicion': fecha_adicion,
        }
        
        return render(request, 'edit_friend.html', data)
    else:
        return redirect('login')

def alert_message(request):
    estado = request.session.get('estado', False)
    if estado:
        # Rescatamos datos de inicio de sesión
        rut_usuario = request.session.get('rut_usuario', None)
        
        # Buscamos el mensaje de alerta del usuario que inició sesión
        usuario = get_usuario_by_rut(rut_usuario)
        mensaje_de_alerta = MensajeDeAlerta.objects.filter(rut_usuario=usuario).values_list('mensaje_alerta')[0][0]
        
        form = forms.EditAlertMessage()

        if request.method == 'POST':
            form = forms.EditAlertMessage(request.POST)
            if form.is_valid():
                nuevo_mensaje = request.POST.get('mensaje_de_alerta')
                # Actualizamos mensaje de alerta
                MensajeDeAlerta.objects.filter(rut_usuario__exact=usuario).update(mensaje_alerta=nuevo_mensaje)
                
                return redirect('home')

        data = {
            'Form': form,
            'rut_usuario': rut_usuario,
            'mensaje_de_alerta': mensaje_de_alerta,
        }
        return render(request, 'alert-message.html', data)
    return redirect('login')

def alert_summary(request):
    estado = request.session.get('estado', False)
    if estado:
        # Rescatamos datos de inicio de sesión
        rut_usuario = request.session.get('rut_usuario', None)
        
        # Rescatamos la información de las alertas emitidas
        alertas_emitidas = Evento.objects.filter(rut_usuario__rut_usuario=rut_usuario).values('hora_evento', 'fecha_evento', 'ubicacion_evento').values_list('hora_evento', 'fecha_evento', 'ubicacion_evento')

        # Obtén la información utilizando la relación indirecta a través de Usuario
        alertas_contactos_emergencia = Evento.objects.filter(
        rut_usuario__detallecontactoemergencia__rut_contacto_emergencia=rut_usuario
            ).values(
                'hora_evento',
                'fecha_evento',
                'ubicacion_evento',
                'rut_usuario__nombre_usuario',
                'rut_usuario__apellido_usuario',
                'rut_usuario__rut_usuario',
                
            ).values_list(
                'hora_evento',
                'fecha_evento',
                'ubicacion_evento',
                'rut_usuario__nombre_usuario',
                'rut_usuario__apellido_usuario',
                'rut_usuario__rut_usuario',
            )

        # Pasamos el detalle de las alertas a listado
        listado_alertas_emitidas, listado_alertas_recibidas = [[str(elemento) for elemento in list(detalle)] for detalle in list(alertas_emitidas)], [[str(elemento) for elemento in list(detalle)] for detalle in list(alertas_contactos_emergencia)]

        # Pasamos datos relevantes
        request.session['alertas_emitidas'] = listado_alertas_emitidas
        request.session['alertas_contactos_emergencia'] = listado_alertas_recibidas
        
        data = {
            'rut_usuario': rut_usuario,
            'alertas_emitidas': listado_alertas_emitidas,
            'alertas_contactos_emergencia': listado_alertas_recibidas,
        }
        
        return render(request, 'alert-summary.html', data)
    else:
        return redirect('login')

def alert_detail(request):
    estado = request.session.get('estado', False)
    if estado:
        # Recuperamos datos relevantes
        rut_usuario = request.session.get('rut_usuario', None)
        
        if rut_usuario is None:
            return redirect('index')
        else:
            if request.method == 'POST':
                alerta_emitida = request.POST.get('alerta_emitida')
                alerta_recibida = request.POST.get('alerta_recibida')
                
                if alerta_emitida is not None:
                    detalle_alerta_emitida = alerta_emitida[1:-1].split(', ')
                    rut = rut_usuario
                    hora_alerta = detalle_alerta_emitida[0][1:-1]
                    fecha_alerta = detalle_alerta_emitida[1][1:-1]
                    frase_alerta = 'emitiste una alerta'
                    coordenadas = detalle_alerta_emitida[2][1:-1].split(',')
                    latitud = coordenadas[0]
                    longitud = coordenadas[1]
                    
                else:
                    detalle_alerta_recibida = alerta_recibida[1:-1].split(', ')
                    rut = detalle_alerta_recibida[5][1:-1]
                    hora_alerta = detalle_alerta_recibida[0][1:-1]
                    fecha_alerta = detalle_alerta_recibida[1][1:-1]
                    frase_alerta = 'emitió una alerta'
                    coordenadas = detalle_alerta_recibida[2][1:-1].split(',')
                    latitud = coordenadas[0]
                    longitud = coordenadas[1]
                    
                usuario = Usuario.objects.get(rut_usuario=rut)
                foto_de_perfil = usuario.foto_de_perfil.url
                nombre_usuario = usuario.nombre_usuario
                apellido_usuario = usuario.apellido_usuario

                # Generamos el mapa
                mapa = folium.Map(location=[latitud, longitud], zoom_start=16)
                # Creamos un marcador
                nuevo_marcador = folium.Marker(
                    location=[latitud, longitud],
                )
            
            nuevo_marcador.add_to(mapa)
            
            mapa_html = mapa._repr_html_()
        
        data = {
            'rut_usuario': rut_usuario,
            'rut': rut,
            'hora_alerta': hora_alerta,
            'fecha_alerta': fecha_alerta,
            'frase_alerta': frase_alerta,
            'foto_de_perfil': foto_de_perfil,
            'mapa_html': mapa_html,
            'nombre_usuario': nombre_usuario,
            'apellido_usuario': apellido_usuario
        }
        
        return render(request, 'alert-detail.html', data)
    return redirect('login')

def profile_template(request):
    estado = request.session.get('estado', False)
    if estado:
        rut_usuario = request.session.get('rut_usuario', None)
        estado_ficha_médica = get_medical_record_status(rut_usuario)
        usuario = get_usuario_by_rut(rut_usuario)
        
        salud_form = forms.SaludForm()
        alergias_form = forms.AlergiasForm()
        discapacidades_form = forms.DiscapacidadesForm()
        medicamentos_form = forms.MedicamentosForm()
        enfermedades_form = forms.EnfermedadesForm()
        estado = request.session.get('estado', False)

        if request.method == 'POST':
            salud_form = forms.SaludForm(request.POST)
            alergias_form = forms.AlergiasForm(request.POST)
            discapacidades_form = forms.DiscapacidadesForm(request.POST)
            medicamentos_form = forms.MedicamentosForm(request.POST)
            enfermedades_form = forms.EnfermedadesForm(request.POST)
            
            if (salud_form.is_valid() and alergias_form.is_valid() and discapacidades_form.is_valid() and
                medicamentos_form.is_valid() and enfermedades_form.is_valid()):
                
                altura = request.POST.get('altura')
                peso = request.POST.get('peso')
                fecha_nacimiento = request.POST.get('fecha_nacimiento')
                alergia = request.POST.get('alergia')
                mostrar_alergia = request.POST.get('mostrar_alergia')
                discapacidad = request.POST.get('discapacidad')
                mostrar_discapacidad = request.POST.get('mostrar_discapacidad')
                medicamento = request.POST.get('medicamento')
                mostrar_medicamento = request.POST.get('mostrar_medicamento')
                enfermedad = request.POST.get('medicamento')
                mostrar_enfermedad = request.POST.get('mostrar_enfermedad')
                
                variables = [mostrar_alergia, mostrar_discapacidad, mostrar_medicamento, mostrar_enfermedad]
                for i, variable in enumerate(variables):
                    if variable == 'on':
                        variables[i] = True
                    else:
                        variables[i] = False
                mostrar_alergia, mostrar_discapacidad, mostrar_medicamento, mostrar_enfermedad = variables
                
                if estado_ficha_médica is None:
                    print('vacio')
                
                    info_salud = InformacionDeSalud(
                        altura=int(altura),
                        peso=int(float(peso)*100),
                        fecha_nacimiento=fecha_nacimiento,
                        rut_usuario=usuario
                    )
                    
                    info_salud.save()
                    
                    DetalleEnfermedad(
                        id_enfermedad=Enfermedad.objects.get(id_enfermedad=int(enfermedad)),
                        id_info_salud=info_salud,
                        mostrar_enfermedad=mostrar_enfermedad
                    ).save()
                    
                    DetalleMedicamento(
                        id_medicamento=Medicamento.objects.get(id_medicamento=int(medicamento)),
                        id_info_salud=info_salud,
                        mostrar_medicamento=mostrar_medicamento
                    ).save()
                    
                    DetalleAlergia(
                        id_alergia=Alergia.objects.get(id_alergia=int(alergia)),
                        id_info_salud=info_salud,
                        mostrar_alergia=mostrar_alergia
                    ).save()
                    
                    DetalleDiscapacidad(
                        id_discapacidad=Discapacidad.objects.get(id_discapacidad=int(discapacidad)),
                        id_info_salud=info_salud,
                        mostrar_discapacidad=mostrar_discapacidad
                    ).save()
                    
                    return redirect('home')
                else:
                    print("hola")
                    DetalleEnfermedad.objects.filter(id_info_salud=estado_ficha_médica.__dict__['id_info_salud']).update(
                        id_enfermedad=Enfermedad.objects.get(id_enfermedad=int(enfermedad)),
                        mostrar_enfermedad=mostrar_enfermedad
                    )
                    
                    DetalleMedicamento.objects.filter(id_info_salud=estado_ficha_médica.__dict__['id_info_salud']).update(
                        id_medicamento=Medicamento.objects.get(id_medicamento=int(medicamento)),
                        mostrar_medicamento=mostrar_medicamento
                    )
                    
                    DetalleAlergia.objects.filter(id_info_salud=estado_ficha_médica.__dict__['id_info_salud']).update(
                        id_alergia=Alergia.objects.get(id_alergia=int(alergia)),
                        mostrar_alergia=mostrar_alergia
                    )
                    
                    DetalleDiscapacidad.objects.filter(id_info_salud=estado_ficha_médica.__dict__['id_info_salud']).update(
                        id_discapacidad=Discapacidad.objects.get(id_discapacidad=int(discapacidad)),
                        mostrar_discapacidad=mostrar_discapacidad
                    )
                    
                    return redirect('home')
                        
        else:
            salud_form = forms.SaludForm()
            alergias_form = forms.AlergiasForm()
            discapacidades_form = forms.DiscapacidadesForm()
            medicamentos_form = forms.MedicamentosForm()
            enfermedades_form = forms.EnfermedadesForm()
            
        data = {
            'salud_form': salud_form,
            'alergias_form': alergias_form,
            'discapacidades_form': discapacidades_form,
            'medicamentos_form': medicamentos_form,
            'enfermedades_form': enfermedades_form,
            }
        
        return render(request, 'profile.html', data)
    else:
        return redirect('login')

def logout_template(request):
    estado = request.session.get('estado', False)
    if estado:
        if request.method == 'POST' and 'salir' in request.POST:
            request.session.clear()
            return redirect('index')
        return render(request, 'logout.html')
    else:
        return redirect('login')

# VER TIPOGRAFIA
# CONFIRMACIÓN DE NUEVO CONTACTO MEDIANTE MAIL
# Nombre socisl yblrgsl