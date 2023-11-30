
from .models import Usuario, InformacionDeSalud, DetalleEnfermedad, Enfermedad, Medicamento, DetalleMedicamento, Alergia, DetalleAlergia, Discapacidad, DetalleDiscapacidad

def get_usuario_by_rut(rut):
    """Instancia un objeto de la clase Usuario.

        Args:
            rut (str): rut chileno del usuario a instanciar.

        Returns:
            usuario: El objeto de Usuario si se encuentra, o None si no se encuentra.
        
        Raises:
            None.
    """
    try:
        usuario = Usuario.objects.get(rut_usuario=rut)
        return usuario
    except Usuario.DoesNotExist:
        return None
    
def get_medical_record_status(rut):
    """Busca si un usuario posee ficha médica
        Args:
            rut (str): rut chilno del usuario
            
        Returns:
            ficha_medica: El objeto de InformacionDeSalud si se encuentra, o None si no se encuentra.
            
        Raises:
            None
    """
    
    try:
        ficha_medica = InformacionDeSalud.objects.get(rut_usuario=rut)
        return ficha_medica
    except InformacionDeSalud.DoesNotExist:
        return None
    
def get_medical_record_details(rut):
    """_summary_

    Args:
        rut (_type_): _description_
    """
    
    informacion_de_salud = get_medical_record_status(rut)
    
    detalle_a_mostrar = {}
    
    if informacion_de_salud is not None:
        # Enfermedad
        try:
            detalle = DetalleEnfermedad.objects.filter(id_info_salud=informacion_de_salud).values()
            if list(detalle)[0]['mostrar_enfermedad']:
                nombre = Enfermedad.objects.filter(id_enfermedad = list(detalle)[0]['id_enfermedad_id']).values()
                nombre = list(nombre)[0]['nombre_enfermedad']
                detalle_a_mostrar['Enfermedad'] = nombre
            
        except DetalleEnfermedad.DoesNotExist:
            detalle_a_mostrar['Enfermedad'] = None
            
        # Medicamento
        try:
            detalle = DetalleMedicamento.objects.filter(id_info_salud=informacion_de_salud).values()
            if list(detalle)[0]['mostrar_medicamento']:
                nombre = Medicamento.objects.filter(id_medicamento = list(detalle)[0]['id_medicamento_id']).values()
                nombre = list(nombre)[0]['nombre_medicamento']
                detalle_a_mostrar['Medicamento'] = nombre
            
        except DetalleMedicamento.DoesNotExist:
            detalle_a_mostrar['Medicamento'] = None
        
        # Alergia
        try:
            detalle = DetalleAlergia.objects.filter(id_info_salud=informacion_de_salud).values()
            if list(detalle)[0]['mostrar_alergia']:
                nombre = Alergia.objects.filter(id_alergia = list(detalle)[0]['id_alergia_id']).values()
                nombre = list(nombre)[0]['nombre_alergia']
                detalle_a_mostrar['Alergia'] = nombre
            
        except DetalleAlergia.DoesNotExist:
            detalle_a_mostrar['Alergia'] = None
            
        # Discapacidad
        try:
            detalle = DetalleDiscapacidad.objects.filter(id_info_salud=informacion_de_salud).values()
            if list(detalle)[0]['mostrar_discapacidad']:
                nombre = Discapacidad.objects.filter(id_discapacidad = list(detalle)[0]['id_discapacidad_id']).values()
                nombre = list(nombre)[0]['nombre_discapacidad']
                detalle_a_mostrar['Discapacidad'] = nombre
            
        except DetalleDiscapacidad.DoesNotExist:
            detalle_a_mostrar['Discapacidad'] = None
            
        return detalle_a_mostrar
    else:
        return None
