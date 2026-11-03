"""Pruebas de RF-06 (catálogo de métricas) y RF-07 (asignación de métricas a un proyecto)."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import MetricaForm
from .models import Metrica, Periodo, Proyecto, Usuario

CLAVES_BASE = ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06"]


def datos_metrica(**cambios):
    datos = {
        "clave": "M-07",
        "nombre": "Densidad de defectos",
        "tipo": "Producto",
        "formula": "defectos / KLOC",
        "unidad": "conteo",
        "meta": "2",
        "sentido": "<=",
        "fuente": "GitHub Issues",
    }
    datos.update(cambios)
    return datos


def crear_metrica_extra():
    return Metrica.objects.create(**{**datos_metrica(), "meta": Decimal("2")})


class MetricasBaseTests(TestCase):
    """RF-07: la migración 0004 carga las 6 métricas base de la sección 7 de la SRS."""

    def test_existen_las_seis_metricas_base(self):
        claves = list(Metrica.objects.filter(es_base=True).values_list("clave", flat=True))
        self.assertEqual(claves, CLAVES_BASE)

    def test_solo_m03_se_cumple_con_menor_o_igual(self):
        sentidos = dict(Metrica.objects.filter(es_base=True).values_list("clave", "sentido"))
        self.assertEqual(sentidos.pop("M-03"), "<=")
        self.assertEqual(set(sentidos.values()), {">="})

    def test_metas_de_la_srs(self):
        metas = dict(Metrica.objects.filter(es_base=True).values_list("clave", "meta"))
        esperadas = {"M-01": 70, "M-02": 95, "M-03": 0, "M-04": 90, "M-05": 100, "M-06": 90}
        self.assertEqual(metas, {clave: Decimal(meta) for clave, meta in esperadas.items()})

    def test_m03_se_mide_en_conteo_y_las_demas_en_porcentaje(self):
        unidades = dict(Metrica.objects.filter(es_base=True).values_list("clave", "unidad"))
        self.assertEqual(unidades.pop("M-03"), "conteo")
        self.assertEqual(set(unidades.values()), {"%"})


class MetaTextoTests(TestCase):
    """La meta se muestra como en los mockups: «≥ 70», «≤ 0», «= 100»."""

    def meta(self, clave):
        return Metrica.objects.get(clave=clave)

    def test_meta_corta(self):
        self.assertEqual(self.meta("M-01").meta_corta, "≥ 70")
        self.assertEqual(self.meta("M-03").meta_corta, "≤ 0")
        self.assertEqual(self.meta("M-05").meta_corta, "= 100")

    def test_meta_texto_agrega_el_porcentaje(self):
        self.assertEqual(self.meta("M-01").meta_texto, "≥ 70 %")
        self.assertEqual(self.meta("M-03").meta_texto, "≤ 0")
        self.assertEqual(self.meta("M-05").meta_texto, "= 100 %")

    def test_decimales_sin_ceros_de_sobra(self):
        metrica = crear_metrica_extra()
        metrica.meta = Decimal("2.50")
        self.assertEqual(metrica.meta_corta, "≤ 2.5")


class CumpleMetaTests(TestCase):
    """El sentido de la meta decide si un valor la cumple (lo usará el reporte de salud)."""

    def test_mayor_o_igual(self):
        cobertura = Metrica.objects.get(clave="M-01")
        self.assertTrue(cobertura.cumple(Decimal("70")))
        self.assertTrue(cobertura.cumple(Decimal("98.4")))
        self.assertFalse(cobertura.cumple(Decimal("69.99")))

    def test_menor_o_igual(self):
        criticos = Metrica.objects.get(clave="M-03")
        self.assertTrue(criticos.cumple(Decimal("0")))
        self.assertFalse(criticos.cumple(Decimal("1")))


class MetricaFormTests(TestCase):
    """RF-06: validación del catálogo en el servidor (RNF-04)."""

    def test_metrica_valida_se_acepta(self):
        self.assertTrue(MetricaForm(data=datos_metrica()).is_valid())

    def test_sin_meta_no_se_guarda(self):
        form = MetricaForm(data=datos_metrica(meta=""))
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["meta"])

    def test_sin_tipo_no_se_guarda(self):
        form = MetricaForm(data=datos_metrica(tipo=""))
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["tipo"])

    def test_tipo_fuera_del_catalogo_se_rechaza(self):
        form = MetricaForm(data=datos_metrica(tipo="Inventado"))
        self.assertFalse(form.is_valid())
        self.assertIn("Selecciona un tipo de la lista.", form.errors["tipo"])

    def test_unidad_fuera_de_la_lista_se_rechaza(self):
        form = MetricaForm(data=datos_metrica(unidad="horas"))
        self.assertFalse(form.is_valid())
        self.assertIn("Selecciona una unidad de la lista.", form.errors["unidad"])

    def test_sentido_invalido_se_rechaza(self):
        form = MetricaForm(data=datos_metrica(sentido="=="))
        self.assertFalse(form.is_valid())
        self.assertIn("sentido", form.errors)

    def test_meta_no_numerica_se_rechaza(self):
        form = MetricaForm(data=datos_metrica(meta="setenta"))
        self.assertFalse(form.is_valid())
        self.assertIn("meta", form.errors)

    def test_meta_negativa_se_rechaza(self):
        form = MetricaForm(data=datos_metrica(meta="-1"))
        self.assertFalse(form.is_valid())
        self.assertIn("La meta no puede ser negativa.", form.errors["meta"])

    def test_porcentaje_mayor_a_100_se_rechaza(self):
        form = MetricaForm(data=datos_metrica(unidad="%", meta="105"))
        self.assertFalse(form.is_valid())
        self.assertIn("Fuera de rango: un porcentaje va de 0 a 100.", form.errors["meta"])

    def test_conteo_mayor_a_100_se_acepta(self):
        self.assertTrue(MetricaForm(data=datos_metrica(unidad="conteo", meta="150")).is_valid())

    def test_nombre_repetido_se_rechaza_sin_importar_mayusculas(self):
        form = MetricaForm(data=datos_metrica(nombre="  cobertura de CÓDIGO "))
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ya existe una métrica con ese nombre en el catálogo.", form.errors["nombre"]
        )

    def test_editar_conserva_su_propio_nombre(self):
        cobertura = Metrica.objects.get(clave="M-01")
        form = MetricaForm(
            data=datos_metrica(
                clave="M-01", nombre="Cobertura de código", unidad="%", meta="75", sentido=">="
            ),
            instance=cobertura,
        )
        self.assertTrue(form.is_valid(), form.errors)


class MetricasBaseVistaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="celeste", password="clave-segura-123"
        )
        cls.lider = Usuario.objects.create(nombre="Ana", perfil="Miembro")
        cls.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def crear_proyecto(self, nombre="Dashboard SQA"):
        return Proyecto.objects.create(
            nombre=nombre,
            descripcion="Descripción de prueba",
            integrantes=4,
            lider=self.lider,
            periodo=self.periodo,
        )


class CatalogoVistasTests(MetricasBaseVistaTest):
    """RF-06: catálogo con el formulario al lado (mockup «Catálogo de métricas»)."""

    def test_lista_muestra_las_metricas_base_y_el_formulario_de_alta(self):
        respuesta = self.client.get(reverse("lista_metricas"))
        self.assertEqual(respuesta.status_code, 200)
        for clave in CLAVES_BASE:
            self.assertContains(respuesta, clave)
        self.assertContains(respuesta, "<h2>Nueva métrica</h2>", html=False)
        self.assertContains(respuesta, "Selecciona una métrica para ver su fórmula.")

    def test_meta_se_muestra_como_en_el_mockup(self):
        respuesta = self.client.get(reverse("lista_metricas"))
        self.assertContains(respuesta, "≥ 70")
        self.assertContains(respuesta, "≤ 0")
        self.assertContains(respuesta, "= 100")

    def test_seleccionar_una_metrica_la_edita_y_muestra_su_formula(self):
        cobertura = Metrica.objects.get(clave="M-01")
        respuesta = self.client.get(reverse("editar_metrica", args=[cobertura.pk]))
        self.assertContains(respuesta, "<h2>Editar M-01</h2>", html=False)
        self.assertContains(respuesta, '<span class="pill gray">Base</span>', html=False)
        self.assertContains(respuesta, "M-01 = líneas cubiertas / líneas totales × 100")
        self.assertContains(respuesta, '<tr class="sel">', count=1, html=False)
        self.assertContains(respuesta, "Celda seleccionada: M-01")

    def test_metrica_no_base_no_lleva_la_etiqueta_base(self):
        extra = crear_metrica_extra()
        respuesta = self.client.get(reverse("editar_metrica", args=[extra.pk]))
        self.assertNotContains(respuesta, '<span class="pill gray">Base</span>', html=False)

    def test_post_valido_registra_la_metrica(self):
        respuesta = self.client.post(reverse("metrica_nueva"), datos_metrica())
        metrica = Metrica.objects.get(clave="M-07")
        self.assertRedirects(respuesta, reverse("editar_metrica", args=[metrica.pk]))
        self.assertEqual(metrica.sentido, "<=")
        self.assertFalse(metrica.es_base)

    def test_post_sin_meta_ni_tipo_no_guarda(self):
        respuesta = self.client.post(reverse("metrica_nueva"), datos_metrica(meta="", tipo=""))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Metrica.objects.filter(clave="M-07").exists())
        self.assertContains(respuesta, "Este campo es obligatorio.", count=2)
        self.assertContains(respuesta, "2 errores en el formulario")

    def test_editar_cambia_solo_esa_metrica(self):
        cobertura = Metrica.objects.get(clave="M-01")
        respuesta = self.client.post(
            reverse("editar_metrica", args=[cobertura.pk]),
            datos_metrica(
                clave="M-01", nombre="Cobertura de código", tipo="Pruebas", unidad="%",
                meta="80", sentido=">=",
            ),
        )
        self.assertRedirects(respuesta, reverse("editar_metrica", args=[cobertura.pk]))
        cobertura.refresh_from_db()
        self.assertEqual(cobertura.meta, Decimal("80"))
        self.assertEqual(Metrica.objects.get(clave="M-04").meta, Decimal("90"))

    def test_editar_metrica_inexistente_da_404(self):
        respuesta = self.client.get(reverse("editar_metrica", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)


class AsignacionMetricasTests(MetricasBaseVistaTest):
    """RF-07: asignar métricas a un proyecto; uno nuevo recibe las 6 métricas base."""

    def claves(self, proyecto):
        return sorted(proyecto.metricas.values_list("clave", flat=True))

    def quitar(self, proyecto, clave):
        metrica = Metrica.objects.get(clave=clave)
        return self.client.post(reverse("quitar_metrica", args=[proyecto.pk, metrica.pk]))

    def test_proyecto_nuevo_recibe_las_metricas_base(self):
        self.assertEqual(self.claves(self.crear_proyecto()), CLAVES_BASE)

    def test_registrar_proyecto_muestra_las_metricas_que_recibira(self):
        respuesta = self.client.get(reverse("proyecto_nuevo"))
        self.assertEqual(
            [m.clave for m in respuesta.context["metricas_base"]], CLAVES_BASE
        )
        self.assertContains(respuesta, "recibe las 6 métricas base del catálogo")

    def test_proyecto_registrado_desde_el_formulario_recibe_las_metricas_base(self):
        self.client.post(
            reverse("proyecto_nuevo"),
            {
                "nombre": "App de inventario",
                "descripcion": "Inventario",
                "lider": self.lider.pk,
                "integrantes": 3,
                "periodo": self.periodo.pk,
            },
        )
        self.assertEqual(self.claves(Proyecto.objects.get(nombre="App de inventario")), CLAVES_BASE)

    def test_metrica_no_base_no_se_asigna_por_defecto(self):
        crear_metrica_extra()
        self.assertNotIn("M-07", self.claves(self.crear_proyecto()))

    def test_editar_el_proyecto_no_reasigna_metricas_quitadas(self):
        proyecto = self.crear_proyecto()
        proyecto.metricas.remove(Metrica.objects.get(clave="M-06"))
        proyecto.descripcion = "Otra descripción"
        proyecto.save()
        self.assertNotIn("M-06", self.claves(proyecto))

    def test_pantalla_lista_las_asignadas_y_ofrece_solo_las_demas(self):
        proyecto = self.crear_proyecto()
        extra = crear_metrica_extra()
        respuesta = self.client.get(reverse("metricas_proyecto", args=[proyecto.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual([m.clave for m in respuesta.context["metricas"]], CLAVES_BASE)
        opciones = respuesta.context["form_asignar"].fields["metrica"].queryset
        self.assertEqual(list(opciones), [extra])
        self.assertContains(respuesta, "6 métricas asignadas")

    def test_pestanas_del_proyecto(self):
        proyecto = self.crear_proyecto()
        respuesta = self.client.get(reverse("metricas_proyecto", args=[proyecto.pk]))
        self.assertContains(respuesta, f'href="{reverse("editar_proyecto", args=[proyecto.pk])}"')
        self.assertContains(respuesta, 'class="tab on"', count=1)
        # Evolución (RF-09) e Historial (RF-18) siguen pendientes.
        self.assertContains(respuesta, 'class="tab off"', count=2)

    def test_post_asigna_una_metrica(self):
        proyecto = self.crear_proyecto()
        extra = crear_metrica_extra()
        respuesta = self.client.post(
            reverse("metricas_proyecto", args=[proyecto.pk]), {"metrica": extra.pk}
        )
        self.assertRedirects(respuesta, reverse("metricas_proyecto", args=[proyecto.pk]))
        self.assertEqual(self.claves(proyecto), [*CLAVES_BASE, "M-07"])

    def test_metrica_ya_asignada_se_rechaza(self):
        proyecto = self.crear_proyecto()
        respuesta = self.client.post(
            reverse("metricas_proyecto", args=[proyecto.pk]),
            {"metrica": Metrica.objects.get(clave="M-01").pk},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Selecciona una métrica del catálogo que no esté asignada.")

    def test_asignar_sin_elegir_muestra_error(self):
        proyecto = self.crear_proyecto()
        respuesta = self.client.post(reverse("metricas_proyecto", args=[proyecto.pk]), {})
        self.assertContains(respuesta, "Selecciona una métrica.")
        self.assertEqual(self.claves(proyecto), CLAVES_BASE)

    def test_metrica_inexistente_se_rechaza(self):
        proyecto = self.crear_proyecto()
        respuesta = self.client.post(
            reverse("metricas_proyecto", args=[proyecto.pk]), {"metrica": 9999}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.claves(proyecto), CLAVES_BASE)

    def test_quitar_una_metrica(self):
        proyecto = self.crear_proyecto()
        respuesta = self.quitar(proyecto, "M-06")
        self.assertRedirects(respuesta, reverse("metricas_proyecto", args=[proyecto.pk]))
        self.assertEqual(self.claves(proyecto), CLAVES_BASE[:5])
        self.assertTrue(Metrica.objects.filter(clave="M-06").exists())

    def test_quitar_no_afecta_a_otros_proyectos(self):
        proyecto = self.crear_proyecto()
        otro = self.crear_proyecto("Otro proyecto")
        for clave in CLAVES_BASE:
            self.quitar(proyecto, clave)
        self.assertEqual(self.claves(proyecto), [])
        self.assertEqual(self.claves(otro), CLAVES_BASE)

    def test_quitar_metrica_no_asignada_da_404(self):
        proyecto = self.crear_proyecto()
        self.quitar(proyecto, "M-06")
        self.assertEqual(self.quitar(proyecto, "M-06").status_code, 404)

    def test_quitar_solo_acepta_post(self):
        proyecto = self.crear_proyecto()
        metrica = Metrica.objects.get(clave="M-01")
        respuesta = self.client.get(reverse("quitar_metrica", args=[proyecto.pk, metrica.pk]))
        self.assertEqual(respuesta.status_code, 405)
        self.assertEqual(self.claves(proyecto), CLAVES_BASE)

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("metricas_proyecto", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse("lista_metricas"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)


class MenuLateralTests(MetricasBaseVistaTest):
    """Menú lateral de los mockups: periodos con sus proyectos activos, catálogos y periodos."""

    def test_muestra_proyectos_activos_por_periodo(self):
        activo = self.crear_proyecto()
        archivado = self.crear_proyecto("Proyecto viejo")
        archivado.estado = Proyecto.Estado.ARCHIVADO
        archivado.save()
        respuesta = self.client.get(reverse("lista_metricas"))
        self.assertContains(respuesta, '<div class="nav-label">Ago-Dic 2026</div>', html=False)
        self.assertContains(respuesta, f'href="{reverse("metricas_proyecto", args=[activo.pk])}"')
        self.assertNotContains(
            respuesta, f'href="{reverse("metricas_proyecto", args=[archivado.pk])}"'
        )

    def test_periodo_mas_reciente_en_la_barra_superior(self):
        Periodo.objects.create(
            nombre="Ene-Jun 2027", fecha_inicio=date(2027, 1, 10), fecha_fin=date(2027, 6, 15)
        )
        respuesta = self.client.get(reverse("lista_metricas"))
        self.assertContains(respuesta, "Periodo: Ene-Jun 2027")

    def test_resalta_el_proyecto_abierto(self):
        proyecto = self.crear_proyecto()
        respuesta = self.client.get(reverse("metricas_proyecto", args=[proyecto.pk]))
        self.assertEqual(respuesta.context["nav_proyecto_actual"], proyecto.pk)
        self.assertContains(respuesta, 'class="tree on"', count=1)

    def test_editar_metrica_no_resalta_ningun_proyecto(self):
        # La vista de métrica también recibe `pk`, pero es de una métrica, no de un proyecto.
        self.crear_proyecto()
        metrica = Metrica.objects.get(clave="M-01")
        respuesta = self.client.get(reverse("editar_metrica", args=[metrica.pk]))
        self.assertIsNone(respuesta.context["nav_proyecto_actual"])
        self.assertNotContains(respuesta, 'class="tree on"')

    def test_paginas_de_metricas_tienen_la_navegacion(self):
        proyecto = self.crear_proyecto()
        paginas = [
            reverse("lista_metricas"),
            reverse("metrica_nueva"),
            reverse("metricas_proyecto", args=[proyecto.pk]),
        ]
        for pagina in paginas:
            with self.subTest(pagina=pagina):
                respuesta = self.client.get(pagina)
                self.assertContains(respuesta, f'href="{reverse("lista_metricas")}"')
                self.assertContains(respuesta, 'action="/logout/"')
