
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from app1.models import Enfermedad, Medicamento, Discapacidad, Alergia

@receiver(post_migrate)
def crear_enfermedades_iniciales(sender, **kwargs):
    if sender.name == 'app1':
        if Enfermedad._meta.db_table not in kwargs.get('using', []):
            enfermedades = [
                Enfermedad(id_enfermedad='1', nombre_enfermedad='Hipertensión'),
                Enfermedad(id_enfermedad='2', nombre_enfermedad='Hipotensión'),
                Enfermedad(id_enfermedad='3', nombre_enfermedad='Agorafobia'),
                Enfermedad(id_enfermedad='4', nombre_enfermedad='Diabetes'),
                Enfermedad(id_enfermedad='5', nombre_enfermedad='Anemia'),
                Enfermedad(id_enfermedad='6', nombre_enfermedad='Asma'),
            ]
            try:
                Enfermedad.objects.bulk_create(enfermedades)
            except:
                pass

    
@receiver(post_migrate)
def crear_medicamentos_iniciales(sender, **kwargs):
    if sender.name == 'app1':
        if Medicamento._meta.db_table not in kwargs.get('using', []):
            medicamentos = [
                Medicamento(id_medicamento='1', nombre_medicamento='Benazepril'),
                Medicamento(id_medicamento='2', nombre_medicamento='Captopril'),
                Medicamento(id_medicamento='3', nombre_medicamento='Amitriptilina'),
                Medicamento(id_medicamento='4', nombre_medicamento='Amoxapina'),
                Medicamento(id_medicamento='5', nombre_medicamento='Escitalopram'),
                Medicamento(id_medicamento='6', nombre_medicamento='Duloxetina'),
            ]
            try:
                Medicamento.objects.bulk_create(medicamentos)
            except:
                pass
     
@receiver(post_migrate)
def crear_medicamentos_iniciales(sender, **kwargs):
    if sender.name == 'app1':
        if Discapacidad._meta.db_table not in kwargs.get('using', []):
            discapacidades = [
                Discapacidad(id_discapacidad='1', nombre_discapacidad='Visual'),
                Discapacidad(id_discapacidad='2', nombre_discapacidad='Auditiva'),
                Discapacidad(id_discapacidad='3', nombre_discapacidad='Cognitiva'),
                Discapacidad(id_discapacidad='4', nombre_discapacidad='Sensorial'),
                Discapacidad(id_discapacidad='5', nombre_discapacidad='Intelectual'),
                Discapacidad(id_discapacidad='6', nombre_discapacidad='Física'),
            ]
            try:
                Discapacidad.objects.bulk_create(discapacidades)
            except:
                pass
            
@receiver(post_migrate)
def crear_alergias_iniciales(sender, **kwargs):
    if sender.name == 'app1':
        if Alergia._meta.db_table not in kwargs.get('using', []):
            alergias = [
                Alergia(id_alergia='1', nombre_alergia='Perros'),
                Alergia(id_alergia='2', nombre_alergia='Gatos'),
                Alergia(id_alergia='3', nombre_alergia='Polvo'),
                Alergia(id_alergia='4', nombre_alergia='Maní'),
                Alergia(id_alergia='5', nombre_alergia='Almendras'),
                Alergia(id_alergia='6', nombre_alergia='Abejas'),
            ]
            try:
                Alergia.objects.bulk_create(alergias)
            except:
                pass