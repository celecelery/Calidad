from django import forms
from django.core.validators import URLValidator
from django.utils import timezone

from .models import (
    AplicacionTecnica,
    AsignacionTecnica,
    Corte,
    Metrica,
    Periodo,
    Proyecto,
    TecnicaSQA,
    Usuario,
)

MENSAJE_OBLIGATORIO = "Este campo es obligatorio."


class PeriodoForm(forms.ModelForm):
    """RF-01: registrar un periodo. Se valida en el servidor (RNF-04)."""

    class Meta:
        model = Periodo
        fields = ["nombre", "fecha_inicio", "fecha_fin"]
        labels = {
            "nombre": "Nombre",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de fin",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
        }
        error_messages = {
            "nombre": {"required": MENSAJE_OBLIGATORIO},
            "fecha_inicio": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid": "Escribe una fecha válida.",
            },
            "fecha_fin": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid": "Escribe una fecha válida.",
            },
        }

    def clean(self):
        datos = super().clean()
        inicio = datos.get("fecha_inicio")
        fin = datos.get("fecha_fin")
        if inicio and fin and fin < inicio:
            self.add_error(
                "fecha_fin",
                "La fecha de fin no puede ser anterior a la fecha de inicio.",
            )
        return datos


class ProyectoForm(forms.ModelForm):
    """RF-02: registrar un proyecto. Se valida en el servidor (RNF-04)."""

    class Meta:
        model = Proyecto
        fields = ["nombre", "descripcion", "lider", "integrantes", "periodo"]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "lider": "Líder",
            "integrantes": "Número de integrantes",
            "periodo": "Periodo",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "lider": forms.Select(attrs={"class": "form-control"}),
            "integrantes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "periodo": forms.Select(attrs={"class": "form-control"}),
        }
        error_messages = {
            "nombre": {"required": MENSAJE_OBLIGATORIO},
            "descripcion": {"required": MENSAJE_OBLIGATORIO},
            "lider": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un líder de la lista.",
            },
            "integrantes": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid": "Escribe un número entero.",
            },
            "periodo": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un periodo de la lista.",
            },
        }

    def clean_nombre(self):
        return self.cleaned_data["nombre"].strip()

    def clean_integrantes(self):
        integrantes = self.cleaned_data["integrantes"]
        if integrantes < 1:
            raise forms.ValidationError("El proyecto debe tener al menos 1 integrante.")
        return integrantes

    def clean(self):
        datos = super().clean()
        nombre = datos.get("nombre")
        periodo = datos.get("periodo")
        if nombre and periodo:
            repetidos = Proyecto.objects.filter(nombre__iexact=nombre, periodo=periodo)
            if self.instance.pk:
                repetidos = repetidos.exclude(pk=self.instance.pk)
            if repetidos.exists():
                self.add_error(
                    "nombre",
                    "Ya existe un proyecto con ese nombre en el periodo seleccionado.",
                )
        return datos


class FiltroProyectosForm(forms.Form):
    """RF-04: filtros de la lista de proyectos por periodo y estado."""

    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.all(),
        required=False,
        empty_label="Todos los periodos",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    estado = forms.ChoiceField(
        choices=[("", "Todos los estados"), *Proyecto.Estado.choices],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

class MetricaForm(forms.ModelForm):
    """RF-06: alta y edición de una métrica del catálogo. No se guarda sin meta ni tipo."""

    class Meta:
        model = Metrica
        fields = ["clave", "nombre", "tipo", "formula", "unidad", "meta", "sentido", "fuente"]
        labels = {
            "clave": "ID",
            "nombre": "Nombre",
            "tipo": "Tipo",
            "formula": "Fórmula",
            "unidad": "Unidad",
            "meta": "Meta",
            "sentido": "Sentido de la meta",
            "fuente": "Fuente de datos",
        }
        widgets = {
            "clave": forms.TextInput(attrs={"class": "input", "placeholder": "M-07"}),
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "tipo": forms.Select(attrs={"class": "input"}),
            "formula": forms.Textarea(attrs={"class": "input", "rows": 2}),
            "unidad": forms.Select(attrs={"class": "input"}),
            "meta": forms.TextInput(attrs={"class": "input", "inputmode": "decimal"}),
            "sentido": forms.RadioSelect,
            "fuente": forms.TextInput(attrs={"class": "input"}),
        }
        error_messages = {
            "nombre": {"required": MENSAJE_OBLIGATORIO},
            "tipo": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un tipo de la lista.",
            },
            "formula": {"required": MENSAJE_OBLIGATORIO},
            "unidad": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona una unidad de la lista.",
            },
            "meta": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid": "Escribe un número.",
            },
            "sentido": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un sentido de la lista.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sin opción vacía preseleccionada: el tipo se elige a propósito.
        self.fields["tipo"].choices = [("", "Selecciona un tipo"), *Metrica.Tipo.choices]
        # La unidad no tiene opción vacía; casi todas las métricas son porcentaje.
        self.fields["unidad"].choices = Metrica.Unidad.choices
        if not self.instance.pk:
            self.initial.setdefault("unidad", Metrica.Unidad.PORCENTAJE)
        # La meta se muestra como en el mockup («90», no «90.00»).
        if self.instance.pk and not self.is_bound:
            self.initial["meta"] = f"{self.instance.meta.normalize():f}"

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        # Se compara en Python: el iexact de SQLite no iguala mayúsculas con acento (Ó / ó).
        otras = Metrica.objects.exclude(pk=self.instance.pk).values_list("nombre", flat=True)
        if any(otra.casefold() == nombre.casefold() for otra in otras):
            raise forms.ValidationError("Ya existe una métrica con ese nombre en el catálogo.")
        return nombre

    def clean_meta(self):
        meta = self.cleaned_data["meta"]
        if meta < 0:
            raise forms.ValidationError("La meta no puede ser negativa.")
        return meta

    def clean(self):
        datos = super().clean()
        meta = datos.get("meta")
        if datos.get("unidad") == Metrica.Unidad.PORCENTAJE and meta is not None and meta > 100:
            self.add_error("meta", "Fuera de rango: un porcentaje va de 0 a 100.")
        return datos


class AsignarMetricaForm(forms.Form):
    """RF-07: asignar a un proyecto una métrica del catálogo que todavía no tenga."""

    metrica = forms.ModelChoiceField(
        queryset=Metrica.objects.none(),
        label="Métrica",
        empty_label="Selecciona una métrica",
        widget=forms.Select(attrs={"class": "input"}),
        error_messages={
            "required": "Selecciona una métrica.",
            "invalid_choice": "Selecciona una métrica del catálogo que no esté asignada.",
        },
    )

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metrica"].queryset = Metrica.objects.exclude(proyectos=proyecto)


def etiquetas_de_cortes(proyecto):
    """«Corte n — dd/mm/aaaa»: los cortes se numeran por fecha dentro de cada proyecto."""
    return {corte.pk: f"Corte {n} — {corte}" for n, corte in enumerate(proyecto.cortes.all(), 1)}


class CorteForm(forms.ModelForm):
    """RF-08: agregar un corte (fecha) al proyecto; debe caer dentro de su periodo."""

    class Meta:
        model = Corte
        fields = ["fecha"]
        labels = {"fecha": "Fecha del corte"}
        widgets = {
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"),
        }
        error_messages = {
            "fecha": {"required": MENSAJE_OBLIGATORIO, "invalid": "Escribe una fecha válida."},
        }

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        self.instance.proyecto = proyecto

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        periodo = self.proyecto.periodo
        if not periodo.fecha_inicio <= fecha <= periodo.fecha_fin:
            raise forms.ValidationError(
                f"El corte debe caer dentro del periodo {periodo.nombre} "
                f"({periodo.fecha_inicio:%d/%m/%Y} – {periodo.fecha_fin:%d/%m/%Y})."
            )
        if self.proyecto.cortes.filter(fecha=fecha).exists():
            raise forms.ValidationError("El proyecto ya tiene un corte en esa fecha.")
        return fecha


class MedicionForm(forms.Form):
    """RF-08: capturar el valor de una métrica en un corte. Se valida en el servidor (RNF-04)."""

    corte = forms.ModelChoiceField(
        queryset=Corte.objects.none(),
        label="Corte",
        empty_label="Selecciona un corte",
        widget=forms.Select(attrs={"class": "input"}),
        error_messages={
            "required": "Selecciona un corte. Si no hay, agrega uno con «+».",
            "invalid_choice": "Selecciona un corte de este proyecto.",
        },
    )
    metrica = forms.ModelChoiceField(
        queryset=Metrica.objects.none(),
        label="Métrica",
        empty_label="Selecciona una métrica",
        widget=forms.Select(attrs={"class": "input"}),
        error_messages={
            "required": "Selecciona una métrica.",
            "invalid_choice": "Selecciona una métrica asignada a este proyecto.",
        },
    )
    valor = forms.DecimalField(
        label="Valor",
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={"class": "input", "inputmode": "decimal"}),
        error_messages={
            "required": MENSAJE_OBLIGATORIO,
            "invalid": "Escribe un número.",
            "max_digits": "El valor es demasiado grande.",
            "max_decimal_places": "Usa como máximo 2 decimales.",
            "max_whole_digits": "El valor es demasiado grande.",
        },
    )

    def __init__(self, *args, proyecto, **kwargs):
        # Ids propios: la misma página tiene el formulario de asignar, que también usa «metrica».
        kwargs.setdefault("auto_id", "med_%s")
        super().__init__(*args, **kwargs)
        etiquetas = etiquetas_de_cortes(proyecto)
        self.fields["corte"].queryset = proyecto.cortes.all()
        self.fields["corte"].label_from_instance = lambda corte: etiquetas[corte.pk]
        self.fields["metrica"].queryset = proyecto.metricas.all()

    def clean(self):
        datos = super().clean()
        metrica = datos.get("metrica")
        valor = datos.get("valor")
        if metrica is None or valor is None:
            return datos
        if metrica.unidad == Metrica.Unidad.PORCENTAJE and not 0 <= valor <= 100:
            self.add_error("valor", "Fuera de rango: un porcentaje va de 0 a 100.")
        elif metrica.unidad == Metrica.Unidad.CONTEO:
            if valor < 0:
                self.add_error("valor", "Fuera de rango: un conteo no puede ser negativo.")
            elif valor != valor.to_integral_value():
                self.add_error("valor", "Un conteo es un número entero.")
        return datos


class TecnicaSQAForm(forms.ModelForm):
    """RF-11: alta y edición de una técnica del catálogo. Se valida en el servidor (RNF-04)."""

    class Meta:
        model = TecnicaSQA
        fields = ["nombre", "descripcion", "referencia_norma"]
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "referencia_norma": "Referencia a norma (opcional)",
        }
        help_texts = {
            "referencia_norma": "Déjalo vacío si la técnica no viene de una norma.",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "descripcion": forms.Textarea(attrs={"class": "input", "rows": 3}),
            "referencia_norma": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "IEEE 1028, ISO/IEC/IEEE 29119, regla del equipo…",
                }
            ),
        }
        error_messages = {
            "nombre": {"required": MENSAJE_OBLIGATORIO},
            "descripcion": {"required": MENSAJE_OBLIGATORIO},
        }

    # Los CharField de Django ya quitan los espacios sobrantes, así que un nombre o una
    # descripción hechos solo de espacios llegan vacíos y fallan como obligatorios.
    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"]
        repetidas = TecnicaSQA.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            repetidas = repetidas.exclude(pk=self.instance.pk)
        if repetidas.exists():
            raise forms.ValidationError("Ya existe una técnica con ese nombre en el catálogo.")
        return nombre


class AsignacionTecnicaForm(forms.ModelForm):
    """RF-12: asignar una técnica a un proyecto con responsable y frecuencia esperada.

    El proyecto no es un campo del formulario: lo fija la vista con la URL. La lista de
    técnicas solo ofrece las que el proyecto todavía no tiene asignadas.
    """

    class Meta:
        model = AsignacionTecnica
        fields = ["tecnica", "usuario", "frecuencia"]
        labels = {
            "tecnica": "Técnica",
            "usuario": "Responsable",
            "frecuencia": "Frecuencia esperada",
        }
        widgets = {
            "tecnica": forms.Select(attrs={"class": "input"}),
            "usuario": forms.Select(attrs={"class": "input"}),
            "frecuencia": forms.RadioSelect,
        }
        error_messages = {
            "tecnica": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona una técnica del catálogo que el proyecto no tenga "
                "asignada.",
            },
            "usuario": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un responsable de la lista.",
            },
            "frecuencia": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona una frecuencia: por corte, por PR o única.",
            },
        }

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        self.instance.proyecto = proyecto
        asignadas = AsignacionTecnica.objects.filter(proyecto=proyecto)
        if self.instance.pk:
            asignadas = asignadas.exclude(pk=self.instance.pk)
        self.fields["tecnica"].queryset = TecnicaSQA.objects.exclude(
            asignaciones__in=asignadas
        ).order_by("nombre")
        self.fields["tecnica"].empty_label = "Selecciona una técnica"
        self.fields["usuario"].queryset = Usuario.objects.order_by("nombre")
        self.fields["usuario"].empty_label = "Selecciona un responsable"
        # Sin la opción vacía "---------" que Django agrega a los radios.
        self.fields["frecuencia"].choices = AsignacionTecnica.Frecuencia.choices


MENSAJE_SIN_EVIDENCIA = (
    "Agrega el enlace al acta, minuta, checklist, PR o documento que demuestra la aplicación."
)


class AplicacionTecnicaForm(forms.ModelForm):
    """RF-13: registrar la aplicación de una técnica asignada al proyecto.

    No se guarda sin enlace de evidencia (RN-12). La fecha debe caer dentro del periodo del
    proyecto y no puede ser futura. Se valida en el servidor (RNF-04).
    """

    class Meta:
        model = AplicacionTecnica
        fields = [
            "asignacion",
            "fecha",
            "registrada_por",
            "resultado",
            "evidencia",
            "observaciones",
        ]
        labels = {
            "asignacion": "Técnica asignada",
            "fecha": "Fecha de aplicación",
            "registrada_por": "Registrada por",
            "resultado": "Resultado",
            "evidencia": "Enlace de evidencia",
            "observaciones": "Observaciones",
        }
        widgets = {
            "asignacion": forms.Select(attrs={"class": "input"}),
            "fecha": forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"),
            "registrada_por": forms.Select(attrs={"class": "input"}),
            "resultado": forms.RadioSelect,
            "evidencia": forms.URLInput(
                attrs={"class": "input", "placeholder": "https://github.com/..."}
            ),
            "observaciones": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }
        error_messages = {
            "asignacion": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona una técnica asignada a este proyecto.",
            },
            "fecha": {"required": MENSAJE_OBLIGATORIO, "invalid": "Escribe una fecha válida."},
            "registrada_por": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un usuario de la lista.",
            },
            "resultado": {
                "required": MENSAJE_OBLIGATORIO,
                "invalid_choice": "Selecciona un resultado: favorable, mixto o no ideal.",
            },
            "evidencia": {
                "required": MENSAJE_SIN_EVIDENCIA,
                "invalid": "Escribe un enlace válido que empiece con https:// o http://.",
                "max_length": "El enlace es demasiado largo (máximo 500 caracteres).",
            },
        }

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        asignaciones = proyecto.asignaciones_tecnicas.select_related("tecnica").order_by(
            "tecnica__nombre"
        )
        campo = self.fields["asignacion"]
        campo.queryset = asignaciones
        campo.empty_label = "Selecciona una técnica"
        campo.label_from_instance = lambda a: f"{a.tecnica.nombre} — {a.frecuencia.lower()}"
        self.fields["registrada_por"].queryset = Usuario.objects.order_by("nombre")
        self.fields["registrada_por"].empty_label = "Selecciona un usuario"
        # Sin la opción vacía "---------" que Django agrega a los radios.
        self.fields["resultado"].choices = AplicacionTecnica.Resultado.choices
        # Solo enlaces web: el URLField de Django también aceptaría ftp://.
        self.fields["evidencia"].validators.append(
            URLValidator(
                schemes=["http", "https"],
                message="Escribe un enlace válido que empiece con https:// o http://.",
            )
        )
        if not self.is_bound:
            self.initial.setdefault("fecha", timezone.localdate())
            asignacion = self.initial.get("asignacion")
            if isinstance(asignacion, AsignacionTecnica):
                # Como en el mockup: se propone al responsable de la técnica.
                self.initial.setdefault("registrada_por", asignacion.usuario)

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        periodo = self.proyecto.periodo
        if not periodo.fecha_inicio <= fecha <= periodo.fecha_fin:
            raise forms.ValidationError(
                f"La fecha debe caer dentro del periodo {periodo.nombre} "
                f"({periodo.fecha_inicio:%d/%m/%Y} – {periodo.fecha_fin:%d/%m/%Y})."
            )
        if fecha > timezone.localdate():
            raise forms.ValidationError("La fecha de aplicación no puede ser futura.")
        return fecha


class PrsFusionadosForm(forms.Form):
    """RF-14: PRs fusionados acumulados a un corte (aplicaciones esperadas «Por PR»)."""

    corte = forms.ModelChoiceField(
        queryset=Corte.objects.none(),
        label="Corte",
        empty_label=None,
        widget=forms.Select(attrs={"class": "input"}),
        error_messages={
            "required": "Selecciona un corte.",
            "invalid_choice": "Selecciona un corte de este proyecto.",
        },
    )
    prs_fusionados = forms.IntegerField(
        label="PRs fusionados al corte",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "input", "min": 0}),
        error_messages={
            "required": MENSAJE_OBLIGATORIO,
            "invalid": "Escribe un número entero.",
            "min_value": "No puede ser negativo.",
        },
    )

    def __init__(self, *args, proyecto, **kwargs):
        kwargs.setdefault("auto_id", "prs_%s")
        super().__init__(*args, **kwargs)
        etiquetas = etiquetas_de_cortes(proyecto)
        self.fields["corte"].queryset = proyecto.cortes.all()
        self.fields["corte"].label_from_instance = lambda corte: etiquetas[corte.pk]
        if not self.is_bound:
            ultimo = proyecto.cortes.last()
            if ultimo:
                self.initial.setdefault("corte", ultimo)
                self.initial.setdefault("prs_fusionados", ultimo.prs_fusionados)

    def clean(self):
        datos = super().clean()
        corte = datos.get("corte")
        prs = datos.get("prs_fusionados")
        if corte is None or prs is None:
            return datos
        # Son acumulados: un corte no puede tener menos PRs que uno anterior ni más que uno
        # posterior.
        anterior = corte.proyecto.cortes.filter(fecha__lt=corte.fecha).last()
        siguiente = corte.proyecto.cortes.filter(fecha__gt=corte.fecha).first()
        if anterior and prs < anterior.prs_fusionados:
            self.add_error(
                "prs_fusionados",
                f"Son acumulados: no pueden ser menos que los {anterior.prs_fusionados} "
                "del corte anterior.",
            )
        elif siguiente and prs > siguiente.prs_fusionados and siguiente.prs_fusionados:
            self.add_error(
                "prs_fusionados",
                f"Son acumulados: no pueden ser más que los {siguiente.prs_fusionados} "
                "del corte siguiente.",
            )
        return datos


class CorteReporteForm(forms.Form):
    """RF-15: elegir el corte del reporte de salud (por omisión, el último)."""

    corte = forms.ModelChoiceField(
        queryset=Corte.objects.none(),
        label="Corte",
        empty_label=None,
        widget=forms.Select(attrs={"class": "input"}),
    )

    def __init__(self, *args, proyecto, **kwargs):
        super().__init__(*args, **kwargs)
        etiquetas = etiquetas_de_cortes(proyecto)
        self.fields["corte"].queryset = proyecto.cortes.all()
        self.fields["corte"].label_from_instance = lambda corte: etiquetas[corte.pk]

