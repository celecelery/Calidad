from django.conf import settings
from django.db import models

# Create your models here.


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    perfil = models.CharField(max_length=100, verbose_name="Perfil")

    def __str__(self):
        return self.nombre


class Periodo(models.Model):
    id_periodo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "Activo", "Activo"
        ARCHIVADO = "Archivado", "Archivado"

    # En el diagrama, 'Nombre' está subrayado dentro del rectángulo del proyecto.
    #pk = models.CompositePrimaryKey("nombre", "id_periodo")

    nombre = models.CharField(
        max_length=150, verbose_name="Nombre del Proyecto"
    )
    integrantes = models.IntegerField(verbose_name="Integrantes")
    descripcion = models.TextField(verbose_name="Descripción")
    estado = models.CharField(
        max_length=50,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        verbose_name="Estado",
    )

    # Relación 'Lidera' con Usuario (1 a N: un usuario lidera varios proyectos)
    lider = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="proyectos_liderados",
        verbose_name="Líder",
    )

    # Relación 'Realizado durante' con Periodo
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name="proyectos",
        verbose_name="Periodo",
    )

    # RF-07: métricas que se le dan seguimiento a este proyecto.
    metricas = models.ManyToManyField(
        "Metrica",
        blank=True,
        related_name="proyectos",
        verbose_name="Métricas asignadas",
    )

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # RF-07: un proyecto nuevo recibe por defecto las métricas base (M-01 a M-06).
        es_nuevo = self._state.adding
        super().save(*args, **kwargs)
        if es_nuevo:
            self.metricas.add(*Metrica.objects.filter(es_base=True))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "periodo"],
                name="proyecto_nombre_unico_por_periodo",
            )
        ]


class ReporteSalud(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    fecha_reporte = models.DateField(verbose_name="Fecha de Reporte")
    corte = models.CharField(max_length=50, verbose_name="Corte")
    semaforo = models.CharField(max_length=50, verbose_name="Semáforo")
    metas_logradas = models.TextField(verbose_name="Metas Logradas")

    # Relación 'Reporte_Proyecto' con Proyecto (1 a N)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="reportes_salud",
        verbose_name="Proyecto",
    )
    

    def __str__(self):
        return f"Reporte {self.id_reporte} - {self.proyecto.nombre}"


class TecnicaSQA(models.Model):
    id_tecnica = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, default="", verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    referencia_norma = models.CharField(
        max_length=150, verbose_name="Referencia de Norma"
    )

    def __str__(self):
        return self.nombre or f"Técnica SQA {self.id_tecnica}"


class AsignacionTecnica(models.Model):
    # Relación que involucra a Proyecto, TécnicasSQA y Usuario con el atributo 'Frecuencia'
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tecnica = models.ForeignKey(TecnicaSQA, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    frecuencia = models.CharField(max_length=50, verbose_name="Frecuencia")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "tecnica", "usuario"],
                name="asignacion_unica",
            )
        ]

class AplicacionTecnica(models.Model):
    id_aplicacion = models.AutoField(primary_key=True)
    fecha = models.DateField(verbose_name="Fecha")
    evidencia = models.TextField(verbose_name="Evidencia")
    resultado = models.CharField(max_length=100, verbose_name="Resultado")

    # Relación con Asignación_Técnica: qué técnica se aplicó y en qué proyecto (RF-13).
    asignacion = models.ForeignKey(
        "AsignacionTecnica",
        on_delete=models.CASCADE,
        related_name="aplicaciones",
        verbose_name="Asignación",
    )

    # Relación 'Registrada_Por' con Usuario
    registrada_por = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="aplicaciones_registradas",
        verbose_name="Registrada por",
    )

    

    def __str__(self):
        return f"Aplicación {self.id_aplicacion} ({self.resultado})"


class Metrica(models.Model):
    """RF-06: catálogo de métricas de calidad (sección 7 de la SRS)."""

    class Tipo(models.TextChoices):
        PRUEBAS = "Pruebas", "Pruebas"
        PRODUCTO = "Producto", "Producto"
        PROCESO = "Proceso", "Proceso"
        GESTION = "Gestión", "Gestión"

    class Sentido(models.TextChoices):
        MAYOR_IGUAL = ">=", "Igual o mayor"
        MENOR_IGUAL = "<=", "Igual o menor"

    class Unidad(models.TextChoices):
        PORCENTAJE = "%", "%"
        CONTEO = "conteo", "conteo"

    id_metrica = models.AutoField(primary_key=True)
    clave = models.CharField(max_length=10, blank=True, verbose_name="Clave")
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    unidad = models.CharField(max_length=50, choices=Unidad.choices, verbose_name="Unidad")
    tipo = models.CharField(max_length=50, choices=Tipo.choices, verbose_name="Tipo")
    formula = models.TextField(verbose_name="Fórmula")
    meta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Meta")
    fuente = models.CharField(max_length=100, blank=True, verbose_name="Fuente")
    sentido = models.CharField(
        max_length=2,
        choices=Sentido.choices,
        default=Sentido.MAYOR_IGUAL,
        verbose_name="Sentido de la meta",
    )
    # RF-07: las métricas base se asignan solas a cada proyecto nuevo.
    es_base = models.BooleanField(default=False, verbose_name="Métrica base")

    class Meta:
        ordering = ["-es_base", "clave", "nombre"]

    def __str__(self):
        return f"{self.clave} {self.nombre}" if self.clave else self.nombre

    @property
    def meta_corta(self):
        """Meta con su sentido, como en los mockups: «≥ 70», «≤ 0», «= 100» (100 % no se rebasa)."""
        if self.sentido == self.Sentido.MENOR_IGUAL:
            simbolo = "≤"
        elif self.unidad == self.Unidad.PORCENTAJE and self.meta == 100:
            simbolo = "="
        else:
            simbolo = "≥"
        return f"{simbolo} {self.meta.normalize():f}"

    @property
    def meta_texto(self):
        """Meta con sentido y, si es porcentaje, su unidad: «≥ 70 %», «≤ 0»."""
        if self.unidad == self.Unidad.PORCENTAJE:
            return f"{self.meta_corta} %"
        return self.meta_corta

    def cumple(self, valor):
        """Indica si un valor medido alcanza la meta según el sentido de la métrica."""
        if self.sentido == self.Sentido.MENOR_IGUAL:
            return valor <= self.meta
        return valor >= self.meta


class Corte(models.Model):
    """RF-08: fecha de corte de un proyecto; en cada corte se captura una medición por métrica.

    El glosario de la SRS define el corte como una fecha (observación (b) de la bitácora #2).
    """

    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="cortes", verbose_name="Proyecto"
    )
    fecha = models.DateField(verbose_name="Fecha de corte")

    class Meta:
        ordering = ["fecha"]
        constraints = [
            models.UniqueConstraint(fields=["proyecto", "fecha"], name="corte_unico_por_fecha"),
        ]

    def __str__(self):
        return self.fecha.strftime("%d/%m/%Y")


class MetricaProyecto(models.Model):
    # Relación 'Métrica_Proyecto' con atributos adicionales 'Valor' y 'Corte' (RF-08: medición)
    #pk = models.CompositePrimaryKey("id_metrica", "id_periodo", "id_proyecto")

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    metrica = models.ForeignKey(Metrica, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    corte = models.ForeignKey(
        Corte, on_delete=models.CASCADE, related_name="mediciones", verbose_name="Corte"
    )
    # Columna «Capturó» del mockup de Mediciones.
    capturado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mediciones_capturadas",
        verbose_name="Capturó",
    )
    capturado_en = models.DateTimeField(auto_now=True, verbose_name="Fecha de captura")

    @property
    def valor_texto(self):
        """Valor como en el mockup: «58 %», «2»."""
        valor = f"{self.valor.normalize():f}"
        return f"{valor} %" if self.metrica.unidad == Metrica.Unidad.PORCENTAJE else valor

    class Meta:
        verbose_name = "Métrica de Proyecto"
        verbose_name_plural = "Métricas de Proyecto"
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "metrica", "corte"],
                name="medicion_unica_por_corte",
            )
        ]