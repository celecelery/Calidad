"""RNF-01: el dashboard carga en menos de 3 s con 20 proyectos (tarea 10.4).

Prueba automatizada de carga: registra 20 proyectos con 3 cortes y sus 6 mediciones base cada
uno, y cronometra la respuesta del servidor para Inicio, la lista de proyectos y el reporte
de salud. No mide el tiempo de red ni de dibujo del navegador: para eso se hace además la
prueba cronometrada en el navegador (matriz de trazabilidad, RNF-01).
"""

import time
from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from dashboard.models import Corte, MetricaProyecto, Periodo, Proyecto, Usuario

LIMITE_SEGUNDOS = 3
PROYECTOS = 20
CORTES = 3


def _cronometrar(cliente, url):
    inicio = time.perf_counter()
    respuesta = cliente.get(url)
    return respuesta.status_code, time.perf_counter() - inicio


@pytest.mark.django_db
def test_rnf01_dashboard_carga_en_menos_de_3_segundos_con_20_proyectos():
    usuario = get_user_model().objects.create_user("qa-rnf01", password="clave-de-prueba-123")
    lider = Usuario.objects.create(user=usuario, nombre="QA", perfil="administrador")
    periodo = Periodo.objects.create(
        nombre="AGO-DIC 2026", fecha_inicio=date(2026, 8, 3), fecha_fin=date(2026, 12, 18)
    )
    for numero in range(1, PROYECTOS + 1):
        proyecto = Proyecto.objects.create(
            nombre=f"Proyecto de carga {numero:02d}",
            integrantes=4,
            descripcion="Proyecto generado para la prueba de carga RNF-01",
            lider=lider,
            periodo=periodo,
        )
        for orden in range(CORTES):
            corte = Corte.objects.create(
                proyecto=proyecto,
                fecha=date(2026, 9, 15) + timedelta(days=21 * orden),
                prs_fusionados=5 * (orden + 1),
            )
            for metrica in proyecto.metricas.all():
                valor = 0 if metrica.unidad == "conteo" else 80
                MetricaProyecto.objects.create(
                    proyecto=proyecto, metrica=metrica, corte=corte, valor=valor
                )

    assert Proyecto.objects.count() == PROYECTOS

    cliente = Client()
    cliente.force_login(usuario)
    primero = Proyecto.objects.order_by("nombre").first()
    pantallas = {
        "Inicio": reverse("inicio"),
        "Lista de proyectos": reverse("lista_proyectos"),
        "Reporte de salud": reverse("reporte_salud", args=[primero.pk]),
        "Historial": reverse("historial_salud", args=[primero.pk]),
    }

    print(f"\nRNF-01: {PROYECTOS} proyectos, {CORTES} cortes y 6 mediciones por corte")
    peor = 0
    for nombre, url in pantallas.items():
        codigo, segundos = _cronometrar(cliente, url)
        print(f"  {nombre:<20} HTTP {codigo}  {segundos:.3f} s")
        assert codigo == 200, f"{nombre} respondió {codigo}"
        peor = max(peor, segundos)
    print(f"  Tiempo máximo: {peor:.3f} s (límite {LIMITE_SEGUNDOS} s)")
    assert peor < LIMITE_SEGUNDOS
