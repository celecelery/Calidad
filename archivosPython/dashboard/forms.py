from django import forms

from .models import Periodo, Proyecto

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