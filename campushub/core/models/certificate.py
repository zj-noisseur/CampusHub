from django.db import models
from .club import Club

class CertificateTemplate(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    template_image = models.ImageField(upload_to='certificates/templates')
    name_x_pos = models.IntegerField(default=500)
    name_y_pos = models.IntegerField(default=500)