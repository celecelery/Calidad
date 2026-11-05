"""Pruebas de integración del flujo completo (tarea 10.3, casos CP-INT-01 a CP-INT-06).

Registrar proyecto -> capturar medición -> generar reporte, recorriendo las pantallas con el
cliente de pruebas de Django, como lo haría un usuario. Cada prueba lleva el ID de su caso en
`Bitacora SQA/casos_de_prueba.md`.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    AsignacionTecnica,
    Corte,
    Metrica,
    MetricaProyecto,
    Periodo,
    Proyecto,
    TecnicaSQA,
    Usuario,
)
from .salud import AMARILLO, ROJO, VERDE

# Valores de M-01 a M-06 que cumplen su meta (M-03 se cumple con 0).
CUMPLEN = {"M-01": "80", "M-02": "97", "M-03": "0", "M-04": "92", "M-05": "100", "M-06": "95"}
EVIDENCIA = "https://github.com/celecelery/Calidad/pull/14"


class FlujoCompletoBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="celeste", password="clave-segura-123"
        )
        # El líder sale del modelo propio `Usuario`, que no tiene pantalla de alta todavía
        # (defecto reportado al probar RF-08; se corrige con RF-20, tarea 6.5).
        cls.lider = Usuario.objects.create(nombre="Angel Mazón", perfil="Administrador")

    def setUp(self):
        self.client.force_login(self.usuario)

    # --- pasos del flujo, cada uno por su pantalla ---

    def post_ok(self, url, datos):
        """Envía un formulario y comprueba que se guardó (redirige en vez de mostrar errores)."""
        respuesta = self.client.post(url, datos)
        if respuesta.status_code != 302:
            errores = {
                nombre: formulario.errors
                for nombre, formulario in (respuesta.context or {}).items()
                if hasattr(formulario, "errors") and formulario.errors
            }
            self.fail(f"El formulario de {url} no se guardó: {errores}")
        return respuesta

    def registrar_proyecto(self):
        self.post_ok(
            reverse("periodo_nuevo"),
            {"nombre": "Ago–Dic 2026", "fecha_inicio": "2026-08-10", "fecha_fin": "2026-12-15"},
        )
        periodo = Periodo.objects.get(nombre="Ago–Dic 2026")
        self.post_ok(
            reverse("proyecto_nuevo"),
            {
                "nombre": "Dashboard SQA",
                "descripcion": "Monitoreo de la calidad del propio proyecto",
                "lider": self.lider.pk,
                "integrantes": 4,
                "periodo": periodo.pk,
            },
        )
        return Proyecto.objects.get(nombre="Dashboard SQA", periodo=periodo)

    def agregar_corte(self, proyecto, fecha):
        self.post_ok(reverse("agregar_corte", args=[proyecto.pk]), {"fecha": fecha})
        return proyecto.cortes.get(fecha=fecha)

    def capturar(self, proyecto, corte, **cambios):
        """Captura M-01 a M-06 en el corte; `cambios` reemplaza valores, p. ej. M_01="60"."""
        valores = {**CUMPLEN, **{clave.replace("_", "-"): v for clave, v in cambios.items()}}
        for clave, valor in valores.items():
            self.capturar_una(proyecto, corte, clave, valor)

    def capturar_una(self, proyecto, corte, clave, valor):
        return self.post_ok(
            reverse("capturar_medicion", args=[proyecto.pk]),
            {"corte": corte.pk, "metrica": Metrica.objects.get(clave=clave).pk, "valor": valor},
        )

    def asignar_tecnica(self, proyecto, nombre="Revisión de pares", frecuencia="Por corte"):
        self.post_ok(
            reverse("tecnicas_proyecto", args=[proyecto.pk]),
            {
                "tecnica": TecnicaSQA.objects.get(nombre=nombre).pk,
                "usuario": self.lider.pk,
                "frecuencia": frecuencia,
            },
        )
        return AsignacionTecnica.objects.get(proyecto=proyecto, tecnica__nombre=nombre)

    def registrar_aplicacion(self, proyecto, asignacion, fecha):
        self.post_ok(
            reverse("registrar_aplicacion", args=[proyecto.pk]),
            {
                "asignacion": asignacion.pk,
                "fecha": fecha,
                "registrada_por": self.lider.pk,
                "resultado": "Favorable",
                "evidencia": EVIDENCIA,
                "observaciones": "",
            },
        )

    def reporte(self, proyecto, corte=None):
        """Abre la pantalla del reporte de salud y devuelve (respuesta, reporte calculado)."""
        datos = {"corte": corte.pk} if corte else {}
        respuesta = self.client.get(reverse("reporte_salud", args=[proyecto.pk]), datos)
        self.assertEqual(respuesta.status_code, 200)
        return respuesta, respuesta.context["reporte"]

    def flujo(self, **cambios):
        """Pasos 1 a 6 del caso CP-INT-01 con un corte el 20/10/2026 y la técnica al día."""
        proyecto = self.registrar_proyecto()
        corte = self.agregar_corte(proyecto, "2026-10-20")
        self.capturar(proyecto, corte, **cambios)
        asignacion = self.asignar_tecnica(proyecto)
        self.registrar_aplicacion(proyecto, asignacion, "2026-10-15")
        return proyecto, corte

    def assertSemaforo(self, respuesta, reporte, color):
        self.assertEqual(reporte.semaforo, color)
        self.assertContains(respuesta, f'aria-label="Semáforo {color}"')


class FlujoCompletoTests(FlujoCompletoBase):
    def test_cp_int_01_flujo_completo_termina_en_verde(self):
        proyecto, corte = self.flujo()

        # El proyecto nuevo recibió las 6 métricas base (RF-07) y quedó todo capturado.
        self.assertEqual(proyecto.metricas.count(), 6)
        self.assertEqual(MetricaProyecto.objects.filter(proyecto=proyecto, corte=corte).count(), 6)

        respuesta, reporte = self.reporte(proyecto)
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (6, 6))
        self.assertEqual(reporte.defectos_criticos, 0)
        self.assertEqual(reporte.porcentaje_tecnicas, 100)
        self.assertSemaforo(respuesta, reporte, VERDE)
        self.assertContains(respuesta, EVIDENCIA)

    def test_cp_int_02_flujo_con_4_de_6_metas_termina_en_amarillo(self):
        proyecto, _ = self.flujo(M_01="60", M_04="85")

        respuesta, reporte = self.reporte(proyecto)
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (4, 6))
        self.assertSemaforo(respuesta, reporte, AMARILLO)

    def test_cp_int_03_flujo_con_un_defecto_critico_termina_en_rojo(self):
        proyecto, _ = self.flujo(M_03="1")

        respuesta, reporte = self.reporte(proyecto)
        self.assertEqual(reporte.defectos_criticos, 1)
        self.assertEqual(reporte.metas_cumplidas, 5)
        self.assertSemaforo(respuesta, reporte, ROJO)
        self.assertContains(respuesta, "defecto crítico abierto")

    def test_cp_int_04_flujo_con_tecnicas_atrasadas_termina_en_rojo(self):
        proyecto = self.registrar_proyecto()
        self.agregar_corte(proyecto, "2026-09-15")
        corte2 = self.agregar_corte(proyecto, "2026-10-20")
        self.capturar(proyecto, corte2)
        asignacion = self.asignar_tecnica(proyecto, frecuencia="Por corte")
        # Por corte espera 2 aplicaciones al corte 2; solo se registra 1 (50 %).
        self.registrar_aplicacion(proyecto, asignacion, "2026-09-10")

        respuesta, reporte = self.reporte(proyecto, corte2)
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (6, 6))
        self.assertEqual(reporte.porcentaje_tecnicas, 50)
        self.assertSemaforo(respuesta, reporte, ROJO)

    def test_cp_int_05_valor_fuera_de_rango_no_llega_al_reporte(self):
        proyecto = self.registrar_proyecto()
        corte = self.agregar_corte(proyecto, "2026-10-20")
        for clave in ("M-02", "M-03", "M-04", "M-05", "M-06"):
            self.capturar_una(proyecto, corte, clave, CUMPLEN[clave])

        rechazo = self.client.post(
            reverse("capturar_medicion", args=[proyecto.pk]),
            {"corte": corte.pk, "metrica": Metrica.objects.get(clave="M-01").pk, "valor": "105"},
        )
        self.assertEqual(rechazo.status_code, 200)
        self.assertContains(rechazo, "Fuera de rango: un porcentaje va de 0 a 100.")
        self.assertFalse(
            MetricaProyecto.objects.filter(proyecto=proyecto, metrica__clave="M-01").exists()
        )

        respuesta, reporte = self.reporte(proyecto)
        self.assertEqual(reporte.sin_medicion, 1)
        self.assertEqual((reporte.metas_cumplidas, reporte.metas_total), (5, 6))
        # Defecto encontrado con este caso: decía «Faltan 1 medicion»; se corrigió la plantilla.
        self.assertContains(
            respuesta, "Falta 1 medición en este corte; cuenta como meta no cumplida."
        )

    def test_cp_int_06_corregir_una_medicion_cambia_el_semaforo(self):
        proyecto, corte = self.flujo(M_01="60", M_04="85")
        respuesta, reporte = self.reporte(proyecto)
        self.assertSemaforo(respuesta, reporte, AMARILLO)

        self.capturar_una(proyecto, corte, "M-01", "75")

        cobertura = MetricaProyecto.objects.get(
            proyecto=proyecto, corte=corte, metrica__clave="M-01"
        )
        self.assertEqual(cobertura.valor, 75)
        self.assertEqual(MetricaProyecto.objects.filter(proyecto=proyecto, corte=corte).count(), 6)
        respuesta, reporte = self.reporte(proyecto)
        self.assertEqual(reporte.metas_cumplidas, 5)
        self.assertSemaforo(respuesta, reporte, VERDE)

    def test_aviso_de_mediciones_faltantes_en_plural(self):
        proyecto = self.registrar_proyecto()
        corte = self.agregar_corte(proyecto, "2026-10-20")
        for clave in ("M-03", "M-04", "M-05", "M-06"):
            self.capturar_una(proyecto, corte, clave, CUMPLEN[clave])

        respuesta, reporte = self.reporte(proyecto)
        self.assertEqual(reporte.sin_medicion, 2)
        self.assertContains(
            respuesta, "Faltan 2 mediciones en este corte; cuentan como metas no cumplidas."
        )

    def test_el_flujo_no_toca_otros_proyectos(self):
        proyecto, _ = self.flujo(M_03="1")
        otro = Proyecto.objects.create(
            nombre="App de inventario",
            descripcion="Otro proyecto",
            integrantes=3,
            lider=self.lider,
            periodo=proyecto.periodo,
        )
        self.assertFalse(Corte.objects.filter(proyecto=otro).exists())
        self.assertFalse(MetricaProyecto.objects.filter(proyecto=otro).exists())
        _, reporte = self.reporte(otro)
        self.assertIsNone(reporte)
