from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Conector, PuntoRecarga


@override_settings(SECURE_SSL_REDIRECT=False)
class PublicMapAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="conductor",
            password="test-password",
        )
        connector = Conector.objects.create(
            codigo=1,
            denominacion="CCS",
            potencia_kw=50,
        )
        cls.points = [
            PuntoRecarga.objects.create(
                nombre=f"Punto predeterminado {index}",
                direccion=f"Calle {index}",
                latitud=f"36.72{index:02d}",
                longitud=f"-4.42{index:02d}",
                tipo_conector=connector,
            )
            for index in range(1, 5)
        ]

    def test_anonymous_api_returns_only_three_safe_points(self):
        response = self.client.get(reverse("api_puntos"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 3)
        self.assertEqual(
            [point["id"] for point in payload],
            [point.pk for point in self.points[:3]],
        )

        private_fields = {
            "reservado",
            "reservado_por",
            "fecha_expiracion",
            "reserva_id",
            "sesion_actual",
            "tiempo_restante",
            "es_reserva_usuario_actual",
            "energia_suministrada_total",
            "energia_actual_sesion",
        }
        self.assertTrue(private_fields.isdisjoint(payload[0]))

    def test_authenticated_api_keeps_full_point_access(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("api_puntos"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 4)
        self.assertIn("reservado", payload[0])
        self.assertIn("sesion_actual", payload[0])

    def test_anonymous_map_is_read_only_and_does_not_request_location(self):
        response = self.client.get(reverse("mapa_puntos_recarga"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estás viendo los puntos predeterminados")
        for point in self.points[:3]:
            self.assertContains(response, point.nombre)
        self.assertNotContains(response, self.points[3].nombre)
        self.assertNotContains(response, "navigator.geolocation.getCurrentPosition")
        self.assertNotContains(response, ">Reservar</button>")
        self.assertNotContains(
            response,
            reverse("detalle_punto_recarga", args=[self.points[0].pk]),
        )

    def test_authenticated_map_can_request_location_and_render_actions(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("mapa_puntos_recarga"))

        self.assertEqual(response.status_code, 200)
        for point in self.points:
            self.assertContains(response, point.nombre)
        self.assertContains(response, "navigator.geolocation.getCurrentPosition")
        self.assertContains(response, ">Reservar</button>")
        self.assertContains(
            response,
            reverse("detalle_punto_recarga", args=[self.points[0].pk]),
        )

    def test_anonymous_user_cannot_create_reservation(self):
        response = self.client.post(
            reverse("api_reservas"),
            data={"punto": self.points[0].pk},
            content_type="application/json",
        )

        self.assertIn(response.status_code, {401, 403})
