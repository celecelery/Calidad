"""Pruebas de los modelos de RF-01 (periodo) y RF-02 (proyecto)."""

from datetime import date

import pytest
from django.db import IntegrityError, transaction

from .models import Periodo, Proyecto, Usuario


@pytest.fixture
def periodo(db):
    return Periodo.objects.create(
        nombre="Ago-Dic 2026", fecha_inicio=date(2026, 8, 10), fecha_fin=date(2026, 12, 15)
    )


@pytest.fixture
def lider(db):
    return Usuario.objects.create(nombre="Ana", perfil="Miembro")


def crear_proyecto(lider, periodo, nombre="Dashboard SQA"):
    return Proyecto.objects.create(
        nombre=nombre,
        integrantes=4,
        descripcion="Monitoreo de calidad",
        estado="Activo",
        lider=lider,
        periodo=periodo,
    )


def test_str_de_proyecto_es_su_nombre(lider, periodo):
    assert str(crear_proyecto(lider, periodo)) == "Dashboard SQA"


def test_base_de_datos_rechaza_nombre_repetido_en_el_mismo_periodo(lider, periodo):
    crear_proyecto(lider, periodo)
    with pytest.raises(IntegrityError), transaction.atomic():
        crear_proyecto(lider, periodo)


def test_base_de_datos_permite_mismo_nombre_en_otro_periodo(lider, periodo):
    otro = Periodo.objects.create(
        nombre="Ene-Jun 2027", fecha_inicio=date(2027, 1, 10), fecha_fin=date(2027, 6, 15)
    )
    crear_proyecto(lider, periodo)
    crear_proyecto(lider, otro)
    assert Proyecto.objects.count() == 2
