from django.contrib.auth.models import AnonymousUser
from django.template.loader import get_template
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from electrolineras.models import Conector, PuntoRecarga
from pages.models import Page


class CookieConsentTemplateTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.user = AnonymousUser()

    def render_base(self):
        return get_template("core/base.html").render({}, self.request)

    def test_cookie_controls_are_available_in_base_template(self):
        html = self.render_base()

        self.assertIn('id="cookie-banner"', html)
        self.assertIn('id="cookie-dialog"', html)
        self.assertIn('data-cookie-action="reject"', html)
        self.assertIn('data-cookie-action="accept"', html)
        self.assertIn('data-cookie-action="save"', html)

    def test_optional_google_fonts_are_deferred(self):
        html = self.render_base()

        self.assertIn('data-cookie-category="preferences"', html)
        self.assertIn('data-cookie-href="https://fonts.googleapis.com/', html)
        self.assertNotIn('<link href="https://fonts.googleapis.com/', html)

    def test_public_contact_details_are_linked(self):
        html = self.render_base()

        self.assertIn('href="mailto:julio@juliomalaga.online"', html)
        self.assertIn(
            'href="briar://ab3xpxsjcfv2jy3dq5xxb4iyhsjpjwius4qlfaga2bgjxqccjflhg"',
            html,
        )
        self.assertNotIn("info@evemaps.com", html)
        self.assertNotIn("+34 123 456 789", html)

    def test_global_seo_metadata_is_available(self):
        html = self.render_base()

        self.assertIn('<meta name="description"', html)
        self.assertIn('<meta name="robots" content="index, follow', html)
        self.assertIn('<link rel="canonical" href="https://evemaps.pythonanywhere.com/">', html)
        self.assertIn('<meta property="og:site_name" content="EvEMaps">', html)


@override_settings(SECURE_SSL_REDIRECT=False)
class SeoPublicEndpointsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        connector = Conector.objects.create(
            codigo=901,
            denominacion="CCS Combo 2",
            potencia_kw=100,
        )
        cls.point = PuntoRecarga.objects.create(
            nombre="Electrolinera Centro",
            direccion="Avenida de la Movilidad, 1",
            latitud="36.721300",
            longitud="-4.421700",
            tipo_conector=connector,
        )
        cls.page = Page.objects.create(
            title="Guía para cargar un coche eléctrico",
            content="<p>Información práctica sobre recarga.</p>",
        )

    def test_robots_txt_publishes_sitemap_and_exclusions(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        self.assertContains(
            response,
            "Sitemap: https://evemaps.pythonanywhere.com/sitemap.xml",
        )
        self.assertContains(response, "Disallow: /admin/")
        self.assertContains(response, "Disallow: /electrolineras/api/")

    def test_google_site_verification_file_is_served_verbatim(self):
        response = self.client.get("/googleabf16e15cc4e6a49.html")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b"google-site-verification: googleabf16e15cc4e6a49.html\n",
        )
        self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_sitemap_contains_canonical_public_urls(self):
        response = self.client.get("/sitemap.xml")
        xml = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("https://testserver/", xml)
        self.assertIn("https://testserver/electrolineras/mapa/", xml)
        self.assertIn(
            f"https://testserver/electrolineras/punto_recarga/{self.point.pk}/",
            xml,
        )
        self.assertIn(
            f"https://testserver/pages/{self.page.pk}/guia-para-cargar-un-coche-electrico/",
            xml,
        )

    def test_home_has_one_descriptive_heading_and_structured_data(self):
        response = self.client.get("/")
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(html.count("<h1"), 1)
        self.assertContains(response, "Encuentra electrolineras y puntos de recarga")
        self.assertContains(response, 'type="application/ld+json"')
        self.assertContains(
            response,
            '<link rel="canonical" href="https://evemaps.pythonanywhere.com/">',
            html=True,
        )

    def test_private_and_technical_routes_receive_noindex_header(self):
        response = self.client.get("/accounts/login/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["X-Robots-Tag"],
            "noindex, nofollow, noarchive",
        )

    def test_public_home_does_not_receive_noindex_header(self):
        response = self.client.get("/")

        self.assertNotIn("X-Robots-Tag", response)

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_http_requests_redirect_to_https(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://testserver/")
