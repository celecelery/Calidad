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
    # En el diagrama, 'Nombre' está subrayado dentro del rectángulo del proyecto.
    #pk = models.CompositePrimaryKey("nombre", "id_periodo")

    nombre = models.CharField(
        max_length=150, verbose_name="Nombre del Proyecto"
    )
    integrantes = models.IntegerField(verbose_name="Integrantes")
    descripcion = models.TextField(verbose_name="Descripción")
    estado = models.CharField(max_length=50, verbose_name="Estado")

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

    def __str__(self):
        return self.nombre
    
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
    descripcion = models.TextField(verbose_name="Descripción")
    referencia_norma = models.CharField(
        max_length=150, verbose_name="Referencia de Norma"
    )

    def __str__(self):
        return f"Técnica SQA {self.id_tecnica}"


class AplicacionTecnica(models.Model):
    id_aplicacion = models.AutoField(primary_key=True)
    fecha = models.DateField(verbose_name="Fecha")
    evidencia = models.TextField(verbose_name="Evidencia")
    resultado = models.CharField(max_length=100, verbose_name="Resultado")

    # Relación 'Registrada_Por' con Usuario
    registrada_por = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="aplicaciones_registradas",
        verbose_name="Registrada por",
    )

    

    def __str__(self):
        return f"Aplicación {self.id_aplicacion} ({self.resultado})"

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

class Metrica(models.Model):
    id_metrica = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    unidad = models.CharField(max_length=50, verbose_name="Unidad")
    tipo = models.CharField(max_length=50, verbose_name="Tipo")
    formula = models.TextField(verbose_name="Fórmula")
    meta = models.CharField(max_length=100, verbose_name="Meta")
    fuente = models.CharField(max_length=100, verbose_name="Fuente")
    sentido = models.CharField(max_length=50, verbose_name="Sentido")

    def __str__(self):
        return self.nombre


class MetricaProyecto(models.Model):
    # Relación 'Métrica_Proyecto' con atributos adicionales 'Valor' y 'Corte'
    #pk = models.CompositePrimaryKey("id_metrica", "id_periodo", "id_proyecto")

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    metrica = models.ForeignKey(Metrica, on_delete=models.CASCADE)
    valor = models.CharField(max_length=100, verbose_name="Valor")
    corte = models.CharField(max_length=50, verbose_name="Corte")

    class Meta:
        verbose_name = "Métrica de Proyecto"
        verbose_name_plural = "Métricas de Proyecto"
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "metrica", "corte"],
                name="medicion_unica_por_corte",
            )
        ]