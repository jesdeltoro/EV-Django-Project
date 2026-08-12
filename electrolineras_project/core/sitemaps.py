from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.text import slugify

from electrolineras.models import PuntoRecarga
from pages.models import Page


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return ("home", "mapa_puntos_recarga", "pages_app:pages")

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {
            "home": 1.0,
            "mapa_puntos_recarga": 0.9,
            "pages_app:pages": 0.7,
        }[item]


class PageSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Page.objects.all().order_by("-updated")

    def lastmod(self, item):
        return item.updated

    def location(self, item):
        return reverse("pages_app:page", args=(item.pk, slugify(item.title)))


class ChargingPointSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PuntoRecarga.objects.all().order_by("nombre")

    def location(self, item):
        return reverse("detalle_punto_recarga", args=(item.pk,))


sitemaps = {
    "static": StaticViewSitemap,
    "articles": PageSitemap,
    "charging-points": ChargingPointSitemap,
}
