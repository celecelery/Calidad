"""RF-11: precarga del catálogo de técnicas SQA (el criterio pide al menos 8).

La referencia a una norma es opcional: se llena solo cuando la técnica viene de una.
Si una técnica con el mismo nombre ya existe, no se duplica ni se sobrescribe.
"""

from django.db import migrations

TECNICAS = [
    (
        "Revisión de pares",
        "Otro integrante revisa el código del pull request antes de integrarlo a main "
        "y aprueba o pide cambios.",
        "IEEE 1028 (revisión técnica)",
    ),
    (
        "Pruebas unitarias",
        "Pruebas automatizadas de funciones, modelos y formularios por separado.",
        "ISO/IEC/IEEE 29119",
    ),
    (
        "Pruebas de integración",
        "Pruebas que verifican que los módulos funcionan juntos (vistas, formularios, "
        "base de datos).",
        "ISO/IEC/IEEE 29119",
    ),
    (
        "Análisis estático",
        "Revisión automática del código sin ejecutarlo (linter en la integración "
        "continua) para detectar errores y problemas de estilo.",
        "",
    ),
    (
        "Checklist de PR",
        "Antes de fusionar, el pull request cumple la lista de verificación acordada "
        "por el equipo (pruebas, linter, cobertura, issue referenciado).",
        "",
    ),
    (
        "Inspección de requisitos",
        "Revisión formal de los requisitos y sus criterios de aceptación para detectar "
        "ambigüedades, contradicciones u omisiones.",
        "IEEE 1028 (inspección)",
    ),
    (
        "Pruebas manuales",
        "Una persona ejecuta los flujos principales en el navegador siguiendo casos de "
        "prueba y registra lo que falla.",
        "ISO/IEC/IEEE 29119",
    ),
    (
        "Auditoría de bitácora",
        "Se verifica que la bitácora SQA esté al día y que cada actividad tenga su "
        "resultado, decisión y evidencia.",
        "IEEE 1028 (auditoría)",
    ),
    (
        "Caminata (walkthrough)",
        "El autor recorre con el equipo un requisito, diseño o código para explicarlo "
        "y encontrar problemas antes de continuar.",
        "IEEE 1028 (walk-through)",
    ),
]


def precargar(apps, schema_editor):
    TecnicaSQA = apps.get_model("dashboard", "TecnicaSQA")
    for nombre, descripcion, referencia in TECNICAS:
        if not TecnicaSQA.objects.filter(nombre__iexact=nombre).exists():
            TecnicaSQA.objects.create(
                nombre=nombre, descripcion=descripcion, referencia_norma=referencia
            )


def quitar(apps, schema_editor):
    TecnicaSQA = apps.get_model("dashboard", "TecnicaSQA")
    # Solo se borran las precargadas que nadie ha asignado a un proyecto.
    TecnicaSQA.objects.filter(
        nombre__in=[nombre for nombre, _, _ in TECNICAS], asignaciones__isnull=True
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0006_tecnicas_catalogo_asignacion"),
    ]

    operations = [
        migrations.RunPython(precargar, quitar),
    ]
