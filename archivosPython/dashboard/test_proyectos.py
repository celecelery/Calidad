"""Pruebas de RF-03 (editar proyecto) y RF-04 (listar proyectos con filtros)."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Periodo, Proyecto, Usuario


class ProyectosBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="angel", password="clave-segura-123"
        )
        cls.ana = Usuario.objects.create(nombre="Ana", perfil="Miembro")
        cls.luis = Usuario.objects.create(nombre="Luis", perfil="Miembro")
        cls.ago_dic = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )
        cls.ene_jun = Periodo.objects.create(
            nombre="Ene-Jun 2027", fecha_inicio=date(2027, 1, 10), fecha_fin=date(2027, 6, 15)
        )
        cls.activo_ago = cls.crear("Dashboard SQA", cls.ago_dic, "Activo", cls.ana)
        cls.archivado_ago = cls.crear("Proyecto viejo", cls.ago_dic, "Archivado", cls.ana)
        cls.activo_ene = cls.crear("App de inventario", cls.ene_jun, "Activo", cls.luis)

    @staticmethod
    def crear(nombre, periodo, estado, lider):
        return Proyecto.objects.create(
            nombre=nombre,
            descripcion="Descripción de prueba",
            integrantes=4,
            estado=estado,
            lider=lider,
            periodo=periodo,
        )

    def setUp(self):
        self.client.force_login(self.usuario)


class ListaProyectosTests(ProyectosBaseTest):
    """RF-04: listar proyectos filtrando por periodo y estado."""

    def nombres(self, respuesta):
        return {proyecto.nombre for proyecto in respuesta.context["proyectos"]}

    def test_sin_filtros_muestra_todos(self):
        respuesta = self.client.get(reverse("lista_proyectos"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            self.nombres(respuesta), {"Dashboard SQA", "Proyecto viejo", "App de inventario"}
        )

    def test_filtra_por_periodo(self):
        respuesta = self.client.get(reverse("lista_proyectos"), {"periodo": self.ago_dic.pk})
        self.assertEqual(self.nombres(respuesta), {"Dashboard SQA", "Proyecto viejo"})

    def test_filtra_por_estado(self):
        respuesta = self.client.get(reverse("lista_proyectos"), {"estado": "Activo"})
        self.assertEqual(self.nombres(respuesta), {"Dashboard SQA", "App de inventario"})

    def test_combina_periodo_y_estado(self):
        respuesta = self.client.get(
            reverse("lista_proyectos"), {"periodo": self.ago_dic.pk, "estado": "Archivado"}
        )
        self.assertEqual(self.nombres(respuesta), {"Proyecto viejo"})

    def test_sin_coincidencias_muestra_mensaje(self):
        respuesta = self.client.get(
            reverse("lista_proyectos"), {"periodo": self.ene_jun.pk, "estado": "Archivado"}
        )
        self.assertEqual(self.nombres(respuesta), set())
        self.assertContains(respuesta, "No hay proyectos que coincidan con los filtros.")

    def test_filtro_invalido_no_truena_y_muestra_todos(self):
        respuesta = self.client.get(reverse("lista_proyectos"), {"periodo": 9999})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(self.nombres(respuesta)), 3)

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse("lista_proyectos"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.url.startswith(reverse("login")))


class EditarProyectoTests(ProyectosBaseTest):
    """RF-03: editar los datos de un proyecto."""

    def datos(self, **cambios):
        datos = {
            "nombre": "Dashboard SQA",
            "descripcion": "Herramienta de monitoreo de calidad",
            "lider": self.ana.pk,
            "integrantes": 4,
            "periodo": self.ago_dic.pk,
        }
        datos.update(cambios)
        return datos

    def url(self, proyecto):
        return reverse("editar_proyecto", args=[proyecto.pk])

    def test_formulario_muestra_los_datos_actuales(self):
        respuesta = self.client.get(self.url(self.activo_ago))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'value="Dashboard SQA"')

    def test_guarda_cambios_y_regresa_a_la_lista(self):
        respuesta = self.client.post(
            self.url(self.activo_ago), self.datos(nombre="Dashboard SQA v2", integrantes=5),
            follow=True,
        )
        self.assertRedirects(respuesta, reverse("lista_proyectos"))
        self.assertContains(respuesta, "Proyecto «Dashboard SQA v2» actualizado.")
        self.activo_ago.refresh_from_db()
        self.assertEqual(self.activo_ago.nombre, "Dashboard SQA v2")
        self.assertEqual(self.activo_ago.integrantes, 5)

    def test_no_modifica_otros_proyectos(self):
        self.client.post(self.url(self.activo_ago), self.datos(nombre="Otro nombre"))
        self.archivado_ago.refresh_from_db()
        self.activo_ene.refresh_from_db()
        self.assertEqual(self.archivado_ago.nombre, "Proyecto viejo")
        self.assertEqual(self.activo_ene.nombre, "App de inventario")

    def test_no_cambia_el_estado_del_proyecto(self):
        self.client.post(self.url(self.archivado_ago), self.datos(nombre="Proyecto viejo"))
        self.archivado_ago.refresh_from_db()
        self.assertEqual(self.archivado_ago.estado, "Archivado")

    def test_sin_nombre_no_guarda(self):
        respuesta = self.client.post(self.url(self.activo_ago), self.datos(nombre=""))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Este campo es obligatorio.")
        self.activo_ago.refresh_from_db()
        self.assertEqual(self.activo_ago.nombre, "Dashboard SQA")

    def test_nombre_repetido_en_el_mismo_periodo_no_guarda(self):
        respuesta = self.client.post(
            self.url(self.activo_ago), self.datos(nombre="Proyecto viejo")
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta, "Ya existe un proyecto con ese nombre en el periodo seleccionado."
        )

    def test_mismo_nombre_en_otro_periodo_si_guarda(self):
        respuesta = self.client.post(
            self.url(self.activo_ago), self.datos(nombre="App de inventario")
        )
        self.assertRedirects(respuesta, reverse("lista_proyectos"))

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("editar_proyecto", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)


class MenuNavegacionTests(ProyectosBaseTest):
    """El menú aparece en todas las páginas con ligas a cada pantalla y botón de cerrar sesión."""

    def test_menu_en_todas_las_paginas(self):
        paginas = [
            reverse("inicio"),
            reverse("lista_proyectos"),
            reverse("editar_proyecto", args=[self.activo_ago.pk]),
            reverse("proyecto_nuevo"),
            reverse("periodo_nuevo"),
        ]
        ligas = ["lista_proyectos", "proyecto_nuevo", "periodo_nuevo", "inicio"]
        for pagina in paginas:
            with self.subTest(pagina=pagina):
                respuesta = self.client.get(pagina)
                self.assertEqual(respuesta.status_code, 200)
                for liga in ligas:
                    self.assertContains(respuesta, f'href="{reverse(liga)}"')
                self.assertContains(respuesta, 'action="/logout/"')


class GraficaInicioTests(ProyectosBaseTest):
    """Gráfica del inicio: proyectos por periodo con datos reales."""

    def test_cuenta_proyectos_por_periodo_y_estado(self):
        from .plotly_app import proyectos_por_periodo

        self.assertEqual(
            proyectos_por_periodo(),
            [
                {"Periodo": "Ago-Dic 2026", "Estado": "Activo", "Proyectos": 1},
                {"Periodo": "Ago-Dic 2026", "Estado": "Archivado", "Proyectos": 1},
                {"Periodo": "Ene-Jun 2027", "Estado": "Activo", "Proyectos": 1},
            ],
        )

    def test_filtra_por_estado(self):
        from .plotly_app import proyectos_por_periodo

        datos = proyectos_por_periodo("Archivado")
        self.assertEqual(
            datos, [{"Periodo": "Ago-Dic 2026", "Estado": "Archivado", "Proyectos": 1}]
        )

    def test_grafica_tiene_una_barra_por_estado(self):
        from .plotly_app import actualizar_grafica

        figura = actualizar_grafica("todos")
        self.assertEqual({barra.name for barra in figura.data}, {"Activo", "Archivado"})

    def test_sin_proyectos_muestra_mensaje(self):
        from .plotly_app import actualizar_grafica

        Proyecto.objects.all().delete()
        figura = actualizar_grafica("todos")
        self.assertEqual(len(figura.data), 0)
        self.assertEqual(figura.layout.annotations[0].text, "Aún no hay proyectos registrados.")
