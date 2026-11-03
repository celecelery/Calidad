"""Pruebas de RF-11 (catálogo de técnicas SQA) y RF-12 (asignar técnicas a un proyecto)."""

from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .forms import AsignacionTecnicaForm, TecnicaSQAForm
from .models import (
    AplicacionTecnica,
    AsignacionTecnica,
    Periodo,
    Proyecto,
    TecnicaSQA,
    Usuario,
)

PRECARGADAS = {
    "Revisión de pares",
    "Pruebas unitarias",
    "Pruebas de integración",
    "Análisis estático",
    "Checklist de PR",
    "Inspección de requisitos",
    "Pruebas manuales",
    "Auditoría de bitácora",
}


class CatalogoPrecargadoTests(TestCase):
    """RF-11, criterio de aceptación: el sistema incluye precargadas al menos 8 técnicas."""

    def test_hay_al_menos_8_tecnicas_precargadas(self):
        self.assertGreaterEqual(TecnicaSQA.objects.count(), 8)

    def test_incluye_las_tecnicas_acordadas(self):
        nombres = set(TecnicaSQA.objects.values_list("nombre", flat=True))
        self.assertTrue(PRECARGADAS <= nombres, PRECARGADAS - nombres)

    def test_todas_tienen_descripcion(self):
        self.assertFalse(TecnicaSQA.objects.filter(descripcion="").exists())

    def test_la_referencia_a_norma_es_opcional(self):
        self.assertTrue(TecnicaSQA.objects.filter(referencia_norma="").exists())
        self.assertTrue(TecnicaSQA.objects.exclude(referencia_norma="").exists())


class TecnicaSQAFormTests(TestCase):
    def datos(self, **cambios):
        datos = {
            "nombre": "Revisión de diseño",
            "descripcion": "Se revisa la arquitectura antes de implementar.",
            "referencia_norma": "",
        }
        datos.update(cambios)
        return datos

    def test_tecnica_valida_sin_referencia_se_acepta(self):
        self.assertTrue(TecnicaSQAForm(data=self.datos()).is_valid())

    def test_campos_obligatorios_muestran_mensaje_en_espanol(self):
        form = TecnicaSQAForm(data={})
        self.assertFalse(form.is_valid())
        for campo in ("nombre", "descripcion"):
            self.assertIn("Este campo es obligatorio.", form.errors[campo])
        self.assertNotIn("referencia_norma", form.errors)

    def test_nombre_o_descripcion_solo_con_espacios_se_rechazan(self):
        form = TecnicaSQAForm(data=self.datos(nombre="   ", descripcion="   "))
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["nombre"])
        self.assertIn("Este campo es obligatorio.", form.errors["descripcion"])

    def test_nombre_repetido_sin_importar_mayusculas_se_rechaza(self):
        form = TecnicaSQAForm(data=self.datos(nombre="  revisión DE pares "))
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Ya existe una técnica con ese nombre en el catálogo.", form.errors["nombre"]
        )

    def test_editar_sin_cambiar_nombre_se_acepta(self):
        tecnica = TecnicaSQA.objects.get(nombre="Revisión de pares")
        form = TecnicaSQAForm(
            data=self.datos(nombre="Revisión de pares", referencia_norma="IEEE 1028"),
            instance=tecnica,
        )
        self.assertTrue(form.is_valid())

    def test_guarda_los_textos_sin_espacios_sobrantes(self):
        form = TecnicaSQAForm(
            data=self.datos(nombre="  Revisión de diseño ", referencia_norma=" IEEE 1028 ")
        )
        self.assertTrue(form.is_valid())
        tecnica = form.save()
        self.assertEqual(tecnica.nombre, "Revisión de diseño")
        self.assertEqual(tecnica.referencia_norma, "IEEE 1028")

    def test_base_de_datos_rechaza_nombre_repetido(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            TecnicaSQA.objects.create(nombre="PRUEBAS UNITARIAS", descripcion="Duplicada")


class TecnicasBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="celeste", password="clave-segura-123"
        )
        cls.ana = Usuario.objects.create(nombre="Ana", perfil="Miembro")
        cls.luis = Usuario.objects.create(nombre="Luis", perfil="Miembro")
        periodo = Periodo.objects.create(
            nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
        )
        cls.proyecto = Proyecto.objects.create(
            nombre="Dashboard SQA",
            descripcion="Monitoreo de calidad",
            integrantes=4,
            lider=cls.ana,
            periodo=periodo,
        )
        cls.otro_proyecto = Proyecto.objects.create(
            nombre="App de inventario",
            descripcion="Otro proyecto",
            integrantes=3,
            lider=cls.luis,
            periodo=periodo,
        )
        cls.revision = TecnicaSQA.objects.get(nombre="Revisión de pares")
        cls.unitarias = TecnicaSQA.objects.get(nombre="Pruebas unitarias")

    def setUp(self):
        self.client.force_login(self.usuario)


class CatalogoVistasTests(TecnicasBaseTest):
    """RF-11: listar, agregar y editar técnicas del catálogo."""

    def test_lista_muestra_las_precargadas(self):
        respuesta = self.client.get(reverse("lista_tecnicas"))
        self.assertEqual(respuesta.status_code, 200)
        for nombre in PRECARGADAS:
            self.assertContains(respuesta, nombre)

    def test_lista_indica_cuando_no_hay_referencia(self):
        respuesta = self.client.get(reverse("lista_tecnicas"))
        self.assertContains(respuesta, "Sin referencia")

    def test_post_valido_agrega_la_tecnica(self):
        respuesta = self.client.post(
            reverse("tecnica_nueva"),
            {"nombre": "Revisión de diseño", "descripcion": "Revisión de la arquitectura."},
        )
        self.assertRedirects(respuesta, reverse("lista_tecnicas"))
        self.assertTrue(TecnicaSQA.objects.filter(nombre="Revisión de diseño").exists())

    def test_post_sin_descripcion_no_guarda(self):
        total = TecnicaSQA.objects.count()
        respuesta = self.client.post(reverse("tecnica_nueva"), {"nombre": "Revisión de diseño"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Este campo es obligatorio.")
        self.assertEqual(TecnicaSQA.objects.count(), total)

    def test_formulario_nuevo_carga(self):
        respuesta = self.client.get(reverse("tecnica_nueva"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "novalidate")

    def test_editar_cambia_solo_esa_tecnica(self):
        descripcion_unitarias = self.unitarias.descripcion
        respuesta = self.client.post(
            reverse("editar_tecnica", args=[self.revision.pk]),
            {
                "nombre": "Revisión de pares",
                "descripcion": "Nueva descripción",
                "referencia_norma": "IEEE 1028",
            },
        )
        self.assertRedirects(respuesta, reverse("lista_tecnicas"))
        self.revision.refresh_from_db()
        self.unitarias.refresh_from_db()
        self.assertEqual(self.revision.descripcion, "Nueva descripción")
        self.assertEqual(self.unitarias.descripcion, descripcion_unitarias)

    def test_editar_carga_los_datos_actuales(self):
        respuesta = self.client.get(reverse("editar_tecnica", args=[self.revision.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Revisión de pares")

    def test_editar_tecnica_inexistente_da_404(self):
        respuesta = self.client.get(reverse("editar_tecnica", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_busqueda_filtra_por_nombre_o_descripcion(self):
        respuesta = self.client.get(reverse("lista_tecnicas"), {"q": "sin ejecutarlo"})
        nombres = [t.nombre for t in respuesta.context["tecnicas"]]
        self.assertEqual(nombres, ["Análisis estático"])
        respuesta = self.client.get(reverse("lista_tecnicas"), {"q": "pruebas"})
        self.assertIn("Pruebas unitarias", [t.nombre for t in respuesta.context["tecnicas"]])

    def test_busqueda_sin_resultados_lo_indica(self):
        respuesta = self.client.get(reverse("lista_tecnicas"), {"q": "zzz"})
        self.assertContains(respuesta, "Ninguna técnica coincide con «zzz».")

    def test_columna_en_uso_cuenta_los_proyectos(self):
        AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        AsignacionTecnica.objects.create(
            proyecto=self.otro_proyecto,
            tecnica=self.revision,
            usuario=self.luis,
            frecuencia="Única",
        )
        respuesta = self.client.get(reverse("lista_tecnicas"))
        en_uso = {t.nombre: t.en_uso for t in respuesta.context["tecnicas"]}
        self.assertEqual(en_uso["Revisión de pares"], 2)
        self.assertEqual(en_uso["Pruebas unitarias"], 0)

    def test_editar_marca_la_fila_y_cambia_el_panel(self):
        respuesta = self.client.get(reverse("editar_tecnica", args=[self.revision.pk]))
        self.assertContains(respuesta, '<tr class="sel">', count=1)
        self.assertContains(respuesta, "Editar técnica")
        self.assertContains(respuesta, "Guardar cambios")

    def test_error_marca_el_campo_en_rojo(self):
        respuesta = self.client.post(reverse("tecnica_nueva"), {"nombre": "revisión de pares"})
        self.assertContains(respuesta, 'class="field con-error"', count=2)
        self.assertContains(respuesta, "Ya existe una técnica con ese nombre en el catálogo.")

    def test_usa_la_plantilla_base_con_estilos_y_cierre_de_sesion(self):
        respuesta = self.client.get(reverse("lista_tecnicas"))
        self.assertTemplateUsed(respuesta, "dashboard/base.html")
        self.assertContains(respuesta, "dashboard/sqa.css")
        self.assertContains(respuesta, 'action="/logout/"')
        self.assertContains(
            respuesta, f'href="{reverse("lista_tecnicas")}" class="on" aria-current="page"'
        )
        self.assertNotContains(respuesta, "Próximamente (RF-11)")

    def test_sin_sesion_redirige_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse("lista_tecnicas"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.url.startswith(reverse("login")))


class AsignacionTecnicaFormTests(TecnicasBaseTest):
    """RF-12, criterio de aceptación: cada asignación tiene responsable y frecuencia."""

    def datos(self, **cambios):
        datos = {
            "tecnica": self.revision.pk,
            "usuario": self.ana.pk,
            "frecuencia": AsignacionTecnica.Frecuencia.POR_PR,
        }
        datos.update(cambios)
        return datos

    def test_asignacion_valida_se_acepta_para_cada_frecuencia(self):
        for frecuencia in AsignacionTecnica.Frecuencia.values:
            with self.subTest(frecuencia=frecuencia):
                form = AsignacionTecnicaForm(
                    data=self.datos(frecuencia=frecuencia), proyecto=self.proyecto
                )
                self.assertTrue(form.is_valid(), form.errors)

    def test_sin_responsable_se_rechaza(self):
        form = AsignacionTecnicaForm(data=self.datos(usuario=""), proyecto=self.proyecto)
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["usuario"])

    def test_sin_frecuencia_se_rechaza(self):
        form = AsignacionTecnicaForm(data=self.datos(frecuencia=""), proyecto=self.proyecto)
        self.assertFalse(form.is_valid())
        self.assertIn("Este campo es obligatorio.", form.errors["frecuencia"])

    def test_frecuencia_fuera_de_las_opciones_se_rechaza(self):
        form = AsignacionTecnicaForm(data=self.datos(frecuencia="Semanal"), proyecto=self.proyecto)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Selecciona una frecuencia: por corte, por PR o única.", form.errors["frecuencia"]
        )

    def test_tecnica_o_responsable_inexistente_se_rechaza(self):
        form = AsignacionTecnicaForm(
            data=self.datos(tecnica=9999, usuario=9999), proyecto=self.proyecto
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Selecciona una técnica del catálogo que el proyecto no tenga asignada.",
            form.errors["tecnica"],
        )
        self.assertIn("Selecciona un responsable de la lista.", form.errors["usuario"])

    def test_misma_tecnica_dos_veces_en_el_proyecto_se_rechaza(self):
        AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        form = AsignacionTecnicaForm(data=self.datos(usuario=self.luis.pk), proyecto=self.proyecto)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Selecciona una técnica del catálogo que el proyecto no tenga asignada.",
            form.errors["tecnica"],
        )

    def test_misma_tecnica_en_otro_proyecto_se_acepta(self):
        AsignacionTecnica.objects.create(
            proyecto=self.otro_proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Única"
        )
        form = AsignacionTecnicaForm(data=self.datos(), proyecto=self.proyecto)
        self.assertTrue(form.is_valid(), form.errors)

    def test_editar_asignacion_sin_cambiar_tecnica_se_acepta(self):
        asignacion = AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        form = AsignacionTecnicaForm(
            data=self.datos(usuario=self.luis.pk, frecuencia="Por corte"),
            instance=asignacion,
            proyecto=self.proyecto,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_solo_ofrece_tecnicas_no_asignadas_al_proyecto(self):
        AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        form = AsignacionTecnicaForm(proyecto=self.proyecto)
        self.assertNotIn(self.revision, form.fields["tecnica"].queryset)
        self.assertIn(self.unitarias, form.fields["tecnica"].queryset)
        otro = AsignacionTecnicaForm(proyecto=self.otro_proyecto)
        self.assertIn(self.revision, otro.fields["tecnica"].queryset)

    def test_frecuencia_son_tres_radios_sin_opcion_vacia(self):
        form = AsignacionTecnicaForm(proyecto=self.proyecto)
        self.assertEqual(
            [valor for valor, _ in form.fields["frecuencia"].choices],
            ["Por corte", "Por PR", "Única"],
        )

    def test_base_de_datos_rechaza_tecnica_repetida_en_el_proyecto(self):
        AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            AsignacionTecnica.objects.create(
                proyecto=self.proyecto, tecnica=self.revision, usuario=self.luis, frecuencia="Única"
            )


class TecnicasProyectoVistaTests(TecnicasBaseTest):
    """RF-12: pantalla de técnicas de un proyecto."""

    def url(self, proyecto=None):
        return reverse("tecnicas_proyecto", args=[(proyecto or self.proyecto).pk])

    def test_pantalla_carga_con_formulario_y_proyecto(self):
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Dashboard SQA")
        self.assertContains(respuesta, "Este proyecto todavía no tiene técnicas asignadas.")
        self.assertContains(respuesta, "novalidate")

    def test_post_valido_crea_la_asignacion_en_ese_proyecto(self):
        respuesta = self.client.post(
            self.url(),
            {"tecnica": self.unitarias.pk, "usuario": self.luis.pk, "frecuencia": "Por corte"},
        )
        self.assertRedirects(respuesta, self.url())
        asignacion = AsignacionTecnica.objects.get()
        self.assertEqual(asignacion.proyecto, self.proyecto)
        self.assertEqual(asignacion.tecnica, self.unitarias)
        self.assertEqual(asignacion.usuario, self.luis)
        self.assertEqual(asignacion.frecuencia, "Por corte")
        mensajes = [str(m) for m in get_messages(respuesta.wsgi_request)]
        self.assertEqual(
            mensajes,
            ["Técnica «Pruebas unitarias» asignada a Luis con frecuencia «Por corte»."],
        )

    def test_post_sin_responsable_no_guarda(self):
        respuesta = self.client.post(
            self.url(), {"tecnica": self.unitarias.pk, "frecuencia": "Por corte"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Este campo es obligatorio.")
        self.assertFalse(AsignacionTecnica.objects.exists())

    def test_lista_solo_las_tecnicas_del_proyecto(self):
        AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        AsignacionTecnica.objects.create(
            proyecto=self.otro_proyecto,
            tecnica=self.unitarias,
            usuario=self.luis,
            frecuencia="Única",
        )
        respuesta = self.client.get(self.url())
        asignaciones = list(respuesta.context["asignaciones"])
        self.assertEqual([a.tecnica for a in asignaciones], [self.revision])
        self.assertContains(respuesta, "Por PR")

    def test_cuenta_las_aplicaciones_registradas(self):
        asignacion = AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        for dia in (1, 2):
            AplicacionTecnica.objects.create(
                asignacion=asignacion,
                fecha=date(2026, 10, dia),
                evidencia="https://github.com/equipo/proyecto/pull/1",
                resultado="Favorable",
                registrada_por=self.ana,
            )
        respuesta = self.client.get(self.url())
        self.assertEqual(respuesta.context["aplicaciones"], 2)
        self.assertEqual(respuesta.context["asignaciones"][0].registradas, 2)

    def test_frecuencia_se_muestra_como_radios(self):
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, 'type="radio"', count=3)

    def test_aviso_cuando_todas_las_tecnicas_estan_asignadas(self):
        for tecnica in TecnicaSQA.objects.all():
            AsignacionTecnica.objects.create(
                proyecto=self.proyecto, tecnica=tecnica, usuario=self.ana, frecuencia="Única"
            )
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, "Todas las técnicas del catálogo ya están asignadas")
        self.assertNotContains(respuesta, 'type="radio"')

    def test_error_de_frecuencia_se_muestra_junto_a_los_radios(self):
        respuesta = self.client.post(
            self.url(), {"tecnica": self.unitarias.pk, "usuario": self.luis.pk}
        )
        self.assertContains(respuesta, '<span class="err-msg">Este campo es obligatorio.</span>')
        self.assertFalse(AsignacionTecnica.objects.exists())

    def test_pestana_tecnicas_activa_y_proyecto_resaltado_en_el_menu(self):
        respuesta = self.client.get(self.url())
        self.assertContains(respuesta, f'href="{self.url()}" aria-current="page">Técnicas SQA</a>')
        self.assertNotContains(respuesta, "Próximamente (RF-12)")
        self.assertEqual(respuesta.context["nav_proyecto_actual"], self.proyecto.pk)

    def test_pestanas_de_otras_secciones_enlazan_a_tecnicas(self):
        respuesta = self.client.get(reverse("metricas_proyecto", args=[self.proyecto.pk]))
        self.assertContains(respuesta, f'href="{self.url()}"')

    def test_proyecto_inexistente_da_404(self):
        respuesta = self.client.get(reverse("tecnicas_proyecto", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_lista_de_proyectos_enlaza_a_sus_tecnicas(self):
        respuesta = self.client.get(reverse("lista_proyectos"))
        self.assertContains(respuesta, self.url())

    def test_str_de_la_asignacion(self):
        asignacion = AsignacionTecnica.objects.create(
            proyecto=self.proyecto, tecnica=self.revision, usuario=self.ana, frecuencia="Por PR"
        )
        self.assertEqual(str(asignacion), "Revisión de pares en Dashboard SQA (Por PR)")
