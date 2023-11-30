from django.test import TestCase

from datetime import datetime

# Create your tests here.
hoy = datetime.now().strftime('%d-%m-%Y')
print(hoy)