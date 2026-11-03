"""Pruebas de RF-13 (registrar la aplicación de una técnica) y RF-14 (cumplimiento)."""

from datetime import date
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .cumplimiento import clase_de_porcentaje, cumplimiento_de_tecnicas
from .forms import AplicacionTecnicaForm, PrsFusionadosForm
from .models import (
    AplicacionTecnica,
    AsignacionTecnica,
    Corte,
    Periodo,
    Proyecto,
    TecnicaSQA,
    Usuario,
)

# Fecha "de hoy" fija para que las pruebas no dependan del día en que se corren.
HOY = date(2026, 11, 3)
EVIDENCIA = "https://github.com/celecelery/Calidad/pull/14"


class TecnicasBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="angel", password="clave-segura-123"
        )
        cls.angel = Usuario.objects.create(nombre="Angel Mazón", perfil="Administrador")
        cls.fernanda = Usuario.objects.create(nombre="Fernanda Méndez", perfil="Miembro")
        cls.periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )
        cls.revision = TecnicaSQA.objects.get(nombre="Revisión de pares")
        cls.unitarias = TecnicaSQA.objects.get(nombre="Pruebas unitarias")
        cls.inspeccion = TecnicaSQA.objects.get(nombre="Inspección de requisitos")

    def setUp(self):
        self.client.force_login(self.usuario)
        self.proyecto = Proyecto.objects.create(
            nombre="Dashboard SQA",
            descripcion="Proyecto de prueba",
            integrantes=4,
            lider=self.angel,
            periodo=self.periodo,
        )
        patcher = mock.patch("dashboard.forms.timezone.localdate", return_value=HOY)
        patcher.start()
        self.addCleanup(patcher.stop)

    def asignar(self, tecnica, frecuencia, usuario=None, proyecto=None):
        return AsignacionTecnica.objects.create(
            proyecto=proyecto or self.proyecto,
            tecnica=tecnica,
            usuario=usuario or self.fernanda,
            frecuencia=frecuencia,
        )

    def corte(self, fecha, prs=0):
        return Corte.objects.create(proyecto=self.proyecto, fecha=fecha, prs_fusionados=prs)

    def aplicar(self, asignacion, fecha, resultado="Favorable"):
        return AplicacionTecnica.objects.create(
            asignacion=asignacion,
            fecha=fecha,
            evidencia=EVIDENCIA,
            resultado=resultado,
            registrada_por=asignacion.usuario,
        )

    def datos(self, elegida, **cambios):
        datos = {
            "asignacion": elegida.pk,
            "fecha": "2026-10-20",
            "registrada_por": self.fernanda.pk,
            "resultado": "Favorable",
            "evidencia": EVIDENCIA,
            "observaciones": "",
        }
        datos.update(cambios)
        return datos


class AplicacionFormTests(TecnicasBase):
    """RF-13: validación en el servidor (RNF-04)."""

    def setUp(self):
        super().setUp()
        self.asignacion = self.asignar(self.revision, "Por PR")

    def form(self, **cambios):
        datos = self.datos(self.asignacion, **cambios)
        return AplicacionTecnicaForm(data=datos, proyecto=self.proyecto)

    def test_aplicacion_valida_se_acepta(self):
        form = self.form(observaciones="3 hallazgos registrados como issues")
        self.assertTrue(form.is_valid(), form.errors)

    def test_sin_enlace_de_evidencia_no_se_guarda(self):
        form = self.form(evidencia="")
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Agrega el enlace al acta, minuta, checklist, PR o documento que demuestra la "
            "aplicación.",
            form.errors["evidencia"],
        )

    def test_evidencia_que_no_es_enlace_se_rechaza(self):
        form = self.form(evidencia="acta de la revisión")
        self.assertFalse(form.is_valid())
        self.assertIn("evidencia", form.errors)

    def test_evidencia_solo_acepta_http_y_https(self):
        form = self.form(evidencia="ftp://servidor/acta.pdf")
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Escribe un enlace válido que empiece con https:// o http://.",
            form.errors["evidencia"],
        )

    def test_campos_obligatorios(self):
        form = self.form(asignacion="", fecha="", registrada_por="", resultado="")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            set(form.errors), {"asignacion", "fecha", "registrada_por", "resultado"}
        )

    def test_observaciones_son_opcionales(self):
        self.assertTrue(self.form(observaciones="").is_valid())

    def test_resultado_fuera_de_la_lista_se_rechaza(self):
        form = self.form(resultado="Excelente")
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Selecciona un resultado: favorable, mixto o no ideal.", form.errors["resultado"]
        )

    def test_fecha_fuera_del_periodo_se_rechaza(self):
        form = self.form(fecha="2026-07-30")
        self.assertFalse(form.is_valid())
        self.assertIn("dentro del periodo Ago-Dic 2026", form.errors["fecha"][0])

    def test_fecha_futura_se_rechaza(self):
        form = self.form(fecha="2026-11-04")
        self.assertFalse(form.is_valid())
        self.assertIn("La fecha de aplicación no puede ser futura.", form.errors["fecha"])

    def test_fecha_de_hoy_se_acepta(self):
        self.assertTrue(self.form(fecha=HOY.isoformat()).is_valid())

    def test_tecnica_de_otro_proyecto_se_rechaza(self):
        otro = Proyecto.objects.create(
            nombre="Otro", descripcion="x", integrantes=1, lider=self.angel, periodo=self.periodo
        )
        ajena = self.asignar(self.unitarias, "Única", proyecto=otro)
        form = self.form(asignacion=ajena.pk)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Selecciona una técnica asignada a este proyecto.", form.errors["asignacion"]
        )

    def test_la_lista_muestra_tecnica_y_frecuencia(self):
        form = AplicacionTecnicaForm(proyecto=self.proyecto)
        opciones = [etiqueta for _, etiqueta in form.fields["asignacion"].choices]
        self.assertIn("Revisión de pares — por pr", opciones)

    def test_propone_al_responsable_de_la_tecnica(self):
        form = AplicacionTecnicaForm(
            proyecto=self.proyecto, initial={"asignacion": self.asignacion}
        )
        self.assertEqual(form.initial["registrada_por"], self.fernanda)
        self.assertEqual(form.initial["fecha"], HOY)


class EsperadasTests(TecnicasBase):
    """RF-14: aplicaciones esperadas según la frecuencia de la asignación (RF-12)."""

    def fila(self, asignacion, corte=None):
        cumplimiento = cumplimiento_de_tecnicas(self.proyecto, corte)
        return next(t for t in cumplimiento.tecnicas if t.asignacion == asignacion)

    def test_unica_espera_una(self):
        asignacion = self.asignar(self.inspeccion, "Única")
        self.assertEqual(self.fila(asignacion).esperadas, 1)

    def test_por_corte_espera_una_por_corte(self):
        asignacion = self.asignar(self.unitarias, "Por corte")
        self.assertEqual(self.fila(asignacion).esperadas, 0)
        for fecha in (date(2026, 9, 15), date(2026, 10, 6), date(2026, 10, 20)):
            self.corte(fecha)
        self.assertEqual(self.fila(asignacion).esperadas, 3)

    def test_por_pr_espera_los_prs_fusionados_al_ultimo_corte(self):
        asignacion = self.asignar(self.revision, "Por PR")
        self.corte(date(2026, 10, 6), prs=3)
        self.corte(date(2026, 10, 20), prs=8)
        self.assertEqual(self.fila(asignacion).esperadas, 8)

    def test_en_un_corte_solo_cuentan_los_cortes_hasta_esa_fecha(self):
        por_corte = self.asignar(self.unitarias, "Por corte")
        por_pr = self.asignar(self.revision, "Por PR")
        primero = self.corte(date(2026, 10, 6), prs=3)
        self.corte(date(2026, 10, 20), prs=8)
        self.assertEqual(self.fila(por_corte, primero).esperadas, 1)
        self.assertEqual(self.fila(por_pr, primero).esperadas, 3)

    def test_en_un_corte_solo_cuentan_las_aplicaciones_hasta_esa_fecha(self):
        asignacion = self.asignar(self.unitarias, "Por corte")
        primero = self.corte(date(2026, 10, 6))
        self.corte(date(2026, 10, 20))
        self.aplicar(asignacion, date(2026, 10, 6))
        self.aplicar(asignacion, date(2026, 10, 15))
        self.assertEqual(self.fila(asignacion, primero).registradas, 1)
        self.assertEqual(self.fila(asignacion).registradas, 2)


class PorcentajeTests(TecnicasBase):
    """RF-14: porcentaje = registradas / esperadas (RN-13)."""

    def test_ejemplo_del_mockup_14_de_18_es_78(self):
        cortes = ((date(2026, 9, 15), 2), (date(2026, 10, 6), 5), (date(2026, 10, 20), 8))
        for fecha, prs in cortes:
            self.corte(fecha, prs)
        revision = self.asignar(self.revision, "Por PR")  # 6 de 8
        caminata = self.asignar(TecnicaSQA.objects.get(nombre="Análisis estático"), "Por corte")
        bitacora = TecnicaSQA.objects.get(nombre="Auditoría de bitácora")
        auditoria = self.asignar(bitacora, "Por corte")
        unitarias = self.asignar(self.unitarias, "Por corte")
        self.asignar(self.inspeccion, "Única")  # 0 de 1
        for dia in range(1, 7):
            self.aplicar(revision, date(2026, 10, dia))
        for asignacion, veces in ((caminata, 2), (auditoria, 3), (unitarias, 3)):
            for dia in range(1, veces + 1):
                self.aplicar(asignacion, date(2026, 9, dia))

        cumplimiento = cumplimiento_de_tecnicas(self.proyecto)
        self.assertEqual((cumplimiento.registradas, cumplimiento.esperadas), (14, 18))
        self.assertEqual(round(cumplimiento.porcentaje), 78)
        porcentajes = [round(t.porcentaje) for t in cumplimiento.tecnicas]
        # Ordenadas por nombre de técnica.
        self.assertEqual(porcentajes, [67, 100, 0, 100, 75])

    def test_mas_aplicaciones_que_las_esperadas_cuenta_como_100(self):
        unica = self.asignar(self.inspeccion, "Única")
        pendiente = self.asignar(self.unitarias, "Única")
        for dia in (1, 2, 3):
            self.aplicar(unica, date(2026, 10, dia))
        cumplimiento = cumplimiento_de_tecnicas(self.proyecto)
        fila = next(t for t in cumplimiento.tecnicas if t.asignacion == unica)
        self.assertEqual(fila.porcentaje, 100)
        # El excedente no compensa a la técnica atrasada: 1 de 2 = 50 %, no 150 %.
        self.assertEqual(cumplimiento.porcentaje, 50)
        self.assertEqual(
            next(t for t in cumplimiento.tecnicas if t.asignacion == pendiente).porcentaje, 0
        )

    def test_sin_esperadas_no_hay_porcentaje(self):
        self.asignar(self.revision, "Por PR")
        cumplimiento = cumplimiento_de_tecnicas(self.proyecto)
        self.assertIsNone(cumplimiento.tecnicas[0].porcentaje)
        self.assertIsNone(cumplimiento.porcentaje)

    def test_sin_tecnicas_asignadas_no_hay_porcentaje(self):
        self.assertIsNone(cumplimiento_de_tecnicas(self.proyecto).porcentaje)

    def test_tecnica_sin_esperadas_no_entra_en_el_total(self):
        self.asignar(self.revision, "Por PR")  # 0 esperadas
        unica = self.asignar(self.inspeccion, "Única")
        self.aplicar(unica, date(2026, 10, 1))
        self.assertEqual(cumplimiento_de_tecnicas(self.proyecto).porcentaje, 100)

    def test_solo_cuenta_las_tecnicas_del_proyecto(self):
        otro = Proyecto.objects.create(
            nombre="Otro", descripcion="x", integrantes=1, lider=self.angel, periodo=self.periodo
        )
        self.asignar(self.inspeccion, "Única", proyecto=otro)
        self.assertEqual(cumplimiento_de_tecnicas(self.proyecto).tecnicas, [])

    def test_color_del_porcentaje(self):
        self.assertEqual(clase_de_porcentaje(80), "good")
        self.assertEqual(clase_de_porcentaje(79.9), "neutral")
        self.assertEqual(clase_de_porcentaje(60), "neutral")
        self.assertEqual(clase_de_porcentaje(59.9), "bad")
        self.assertEqual(clase_de_porcentaje(None), "")


class RegistrarAplicacionVistaTests(TecnicasBase):
    def setUp(self):
        super().setUp()
        self.asignacion = self.asignar(self.unitarias, "Por corte")
        self.corte(date(2026, 10, 6))
        self.corte(date(2026, 10, 20))
        self.url = reverse("registrar_aplicacion", args=[self.proyecto.pk])

    def test_desde_la_tabla_llega_con_la_tecnica_elegida(self):
        respuesta = self.client.get(self.url, {"asignacion": self.asignacion.pk})
        self.assertEqual(respuesta.status_code, 200)
        formulario = respuesta.context["formulario"]
        self.assertEqual(formulario.initial["asignacion"], self.asignacion)
        self.assertEqual(formulario.initial["registrada_por"], self.fernanda)
        self.assertEqual(respuesta.context["detalle"]["fila"].esperadas, 2)

    def test_panel_lista_las_aplicaciones_con_su_corte(self):
        self.aplicar(self.asignacion, date(2026, 10, 3), resultado="Mixto")
        respuesta = self.client.get(self.url, {"asignacion": self.asignacion.pk})
        self.assertContains(respuesta, "03/10/2026 · Corte 1")
        self.assertContains(respuesta, f'href="{EVIDENCIA}"')
        self.assertContains(respuesta, "1 de 2 · 50 %")

    def test_asignacion_ajena_o_invalida_no_se_preselecciona(self):
        respuesta = self.client.get(self.url, {"asignacion": "abc"})
        self.assertIsNone(respuesta.context["detalle"])

    def test_post_valido_guarda_y_regresa_a_tecnicas(self):
        respuesta = self.client.post(self.url, self.datos(self.asignacion))
        self.assertRedirects(respuesta, reverse("tecnicas_proyecto", args=[self.proyecto.pk]))
        aplicacion = AplicacionTecnica.objects.get()
        self.assertEqual(aplicacion.evidencia, EVIDENCIA)
        self.assertEqual(aplicacion.registrada_por, self.fernanda)
        mensajes = [str(m) for m in get_messages(respuesta.wsgi_request)]
        self.assertIn(
            "Aplicación de «Pruebas unitarias» registrada. Lleva 1 de 2 (50 %).", mensajes
        )

    def test_post_sin_evidencia_no_guarda_y_lo_dice(self):
        respuesta = self.client.post(self.url, self.datos(self.asignacion, evidencia=""))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(AplicacionTecnica.objects.exists())
        self.assertContains(respuesta, "No se guardó: falta el enlace de evidencia.")
        self.assertContains(respuesta, "1 error en el formulario")

    def test_sin_tecnicas_asignadas_avisa(self):
        self.asignacion.delete()
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, "El proyecto no tiene técnicas asignadas.")

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("registrar_aplicacion", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)


class PestanaTecnicasCumplimientoTests(TecnicasBase):
    def setUp(self):
        super().setUp()
        self.url = reverse("tecnicas_proyecto", args=[self.proyecto.pk])

    def test_muestra_esperadas_registradas_y_porcentaje(self):
        asignacion = self.asignar(self.unitarias, "Por corte")
        self.corte(date(2026, 10, 6))
        self.corte(date(2026, 10, 20))
        self.aplicar(asignacion, date(2026, 10, 6))
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.context["cumplimiento"].porcentaje, 50)
        self.assertContains(respuesta, '<td class="num bad">50 %</td>', html=False)
        self.assertContains(respuesta, "Total del proyecto")
        self.assertContains(respuesta, "Cumplimiento de técnicas: 50 %")
        registrar = reverse("registrar_aplicacion", args=[self.proyecto.pk])
        self.assertContains(respuesta, f"{registrar}?asignacion={asignacion.pk}")

    def test_sin_tecnicas_no_hay_porcentaje(self):
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, "Sin aplicaciones esperadas todavía")

    def test_formulario_de_prs_solo_si_hay_tecnicas_por_pr(self):
        self.corte(date(2026, 10, 6))
        self.asignar(self.unitarias, "Por corte")
        self.assertNotContains(self.client.get(self.url), "PRs fusionados por corte")
        self.asignar(self.revision, "Por PR")
        self.assertContains(self.client.get(self.url), "PRs fusionados por corte")


class PrsFusionadosTests(TecnicasBase):
    def setUp(self):
        super().setUp()
        self.asignar(self.revision, "Por PR")
        self.primero = self.corte(date(2026, 10, 6), prs=3)
        self.segundo = self.corte(date(2026, 10, 20), prs=8)
        self.url = reverse("guardar_prs_fusionados", args=[self.proyecto.pk])

    def form(self, corte, prs):
        return PrsFusionadosForm(
            data={"corte": corte.pk, "prs_fusionados": prs}, proyecto=self.proyecto
        )

    def test_guardar_actualiza_el_corte(self):
        respuesta = self.client.post(self.url, {"corte": self.segundo.pk, "prs_fusionados": 10})
        self.assertRedirects(respuesta, reverse("tecnicas_proyecto", args=[self.proyecto.pk]))
        self.segundo.refresh_from_db()
        self.assertEqual(self.segundo.prs_fusionados, 10)

    def test_negativo_se_rechaza(self):
        form = self.form(self.segundo, -1)
        self.assertFalse(form.is_valid())
        self.assertIn("No puede ser negativo.", form.errors["prs_fusionados"])

    def test_no_pueden_ser_menos_que_el_corte_anterior(self):
        form = self.form(self.segundo, 2)
        self.assertFalse(form.is_valid())
        self.assertIn("corte anterior", form.errors["prs_fusionados"][0])

    def test_no_pueden_ser_mas_que_el_corte_siguiente(self):
        form = self.form(self.primero, 9)
        self.assertFalse(form.is_valid())
        self.assertIn("corte siguiente", form.errors["prs_fusionados"][0])

    def test_corte_de_otro_proyecto_se_rechaza(self):
        otro = Proyecto.objects.create(
            nombre="Otro", descripcion="x", integrantes=1, lider=self.angel, periodo=self.periodo
        )
        ajeno = Corte.objects.create(proyecto=otro, fecha=date(2026, 10, 6))
        self.assertFalse(self.form(ajeno, 1).is_valid())

    def test_post_con_error_vuelve_a_la_pestana_con_el_formulario_abierto(self):
        respuesta = self.client.post(self.url, {"corte": self.segundo.pk, "prs_fusionados": ""})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["abrir_prs"])
        self.assertContains(respuesta, "error en los PRs fusionados")

    def test_solo_acepta_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
