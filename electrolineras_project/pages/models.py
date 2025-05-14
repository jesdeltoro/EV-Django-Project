from django.db import models
from tinymce.models import HTMLField  # Cambiado para usar TinyMCE

class Page(models.Model):
    title = models.CharField(verbose_name="Título", max_length=200)
    content = HTMLField(verbose_name="Contenido")  # Cambiado a HTMLField
    order = models.SmallIntegerField(verbose_name="Orden", default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")

    class Meta:
        verbose_name = "página"
        verbose_name_plural = "páginas"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
