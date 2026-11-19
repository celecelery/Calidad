"""RF-17: exportar el reporte de salud (RF-15) a PDF.

El PDF lleva lo mismo que la pantalla del reporte: el semáforo con su motivo, los indicadores
(metas, defectos críticos y técnicas), la tabla de métricas contra meta con la comparación
contra el corte anterior (RF-16) y el cumplimiento de técnicas SQA con sus enlaces de
evidencia.

Formato de una página tipo «informe ejecutivo», con la paleta turquesa del sistema (sqa.css):
banda de encabezado, paneles con barra de título, medidores circulares para los indicadores,
puntos de color en el diagnóstico, pastillas «Sí/No» y barras de avance en las técnicas.

Se arma con ReportLab. Se usa la fuente Vera que viene dentro de ReportLab porque las fuentes
estándar de PDF no tienen los símbolos «≥» y «≤» de las metas; así funciona igual en Windows,
en Linux y en el CI sin instalar fuentes.

Los textos de las tablas se calculan aparte (``filas_de_metricas``, ``filas_de_tecnicas`` e
``indicadores``) para poder probarlos sin leer el PDF.
"""

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import reportlab
from django.utils import timezone
from django.utils.text import slugify
from reportlab.graphics.shapes import Circle, Drawing, Rect, String, Wedge
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .cumplimiento import clase_de_porcentaje
from .salud import (
    AMARILLO,
    CLASE_TENDENCIA,
    METAS_ROJO,
    METAS_VERDE,
    ROJO,
    TECNICAS_VERDE,
    VERDE,
)

# --- Fuentes ---
_CARPETA_FUENTES = Path(reportlab.__file__).parent / "fonts"
FUENTE = "Vera"
FUENTE_NEGRITA = "Vera-Bold"

# --- Colores: los mismos de sqa.css ---
VERDE_SQA = colors.HexColor("#00838f")  # --verde (barra superior del sistema)
VERDE_OSC = colors.HexColor("#005f66")  # --verde-osc
VERDE_CLARO = colors.HexColor("#e0f4f5")  # --verde-claro
VERDE_BORDE = colors.HexColor("#8fd3d8")  # --verde-borde
FONDO_TARJETA = colors.HexColor("#f4fbfb")
TEXTO = colors.HexColor("#201f1e")
TEXTO_2 = colors.HexColor("#323130")
GRIS_TEXTO = colors.HexColor("#605e5c")
LINEA = colors.HexColor("#e1dfdd")
GRIS_VACIO = colors.HexColor("#edebe9")
LUZ_APAGADA = colors.HexColor("#55534f")
ENLACE = "#005f66"

# Estado → (color fuerte, fondo de pastilla, texto de pastilla), como .pill y .luz en sqa.css.
ESTADOS = {
    "good": (colors.HexColor("#00b050"), colors.HexColor("#c6efce"), colors.HexColor("#006100")),
    "neutral": (colors.HexColor("#ffc000"), colors.HexColor("#ffeb9c"), colors.HexColor("#9c5700")),
    "bad": (colors.HexColor("#e81123"), colors.HexColor("#ffc7ce"), colors.HexColor("#9c0006")),
    "": (colors.HexColor("#a19f9d"), GRIS_VACIO, TEXTO_2),
}
ESTADOS["gray"] = ESTADOS[""]  # .pill.gray de sqa.css
CLASE_SEMAFORO = {ROJO: "bad", AMARILLO: "neutral", VERDE: "good"}

SIN_DATO = "—"
ALTO_BANDA = 30 * mm
MARGEN = 14 * mm


def _registrar_fuentes():
    if FUENTE in pdfmetrics.getRegisteredFontNames():
        return
    pdfmetrics.registerFont(TTFont(FUENTE, str(_CARPETA_FUENTES / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont(FUENTE_NEGRITA, str(_CARPETA_FUENTES / "VeraBd.ttf")))
    pdfmetrics.registerFontFamily(
        FUENTE, normal=FUENTE, bold=FUENTE_NEGRITA, italic=FUENTE, boldItalic=FUENTE_NEGRITA
    )


def _estilo(nombre, **opciones):
    base = {"fontName": FUENTE, "fontSize": 8.5, "leading": 11, "textColor": TEXTO_2}
    return ParagraphStyle(nombre, **{**base, **opciones})


ESTILOS = {
    "panel": _estilo("panel", fontName=FUENTE_NEGRITA, fontSize=9, textColor=colors.white),
    "seccion": _estilo(
        "seccion", fontName=FUENTE_NEGRITA, fontSize=10, leading=13, textColor=colors.white
    ),
    "celda": _estilo("celda"),
    "encabezado": _estilo("encabezado", fontName=FUENTE_NEGRITA, fontSize=8, textColor=VERDE_OSC),
    "clave": _estilo("clave", fontName=FUENTE_NEGRITA, textColor=VERDE_OSC),
    "k": _estilo("k", fontName=FUENTE_NEGRITA, fontSize=8.5, leading=11, textColor=VERDE_OSC),
    "h": _estilo("h", fontSize=7.5, leading=10, textColor=GRIS_TEXTO),
    "objetivo": _estilo("objetivo", fontSize=7.5, leading=10, textColor=TEXTO_2),
    "motivo": _estilo("motivo", fontName=FUENTE_NEGRITA, fontSize=9, leading=12, textColor=TEXTO),
    "punto": _estilo("punto", fontSize=8.5, leading=11),
}


def _pct(valor):
    return SIN_DATO if valor is None else f"{valor:.0f} %"


def _clase_metas(porcentaje):
    """Mismos cortes del semáforo: Verde desde 83 %, Rojo debajo de 50 %."""
    if porcentaje is None:
        return ""
    if porcentaje >= METAS_VERDE:
        return "good"
    return "neutral" if porcentaje >= METAS_ROJO else "bad"


def _clase_defectos(criticos):
    if criticos is None:
        return ""
    return "good" if criticos == 0 else "bad"


# --- Datos del reporte, en texto ---


def indicadores(reporte):
    """Los tres indicadores de la pantalla: (título, valor, ayuda)."""
    metas_ayuda = "" if reporte.porcentaje_metas is None else _pct(reporte.porcentaje_metas)
    if reporte.sin_medicion:
        metas_ayuda += f"{' · ' if metas_ayuda else ''}{reporte.sin_medicion} sin medición"

    criticos = reporte.defectos_criticos
    tecnicas = reporte.tecnicas
    return [
        ("Metas cumplidas", f"{reporte.metas_cumplidas} / {reporte.metas_total}", metas_ayuda),
        (
            "Defectos críticos",
            SIN_DATO if criticos is None else f"{criticos:.0f}",
            "M-03 sin medición en este corte"
            if criticos is None
            else "M-03 · issues críticos abiertos",
        ),
        (
            "Técnicas SQA",
            _pct(reporte.porcentaje_tecnicas),
            f"{tecnicas.registradas if tecnicas else 0} de "
            f"{tecnicas.esperadas if tecnicas else 0} aplicaciones",
        ),
    ]


def aviso_mediciones_faltantes(reporte):
    """El mismo aviso de la pantalla cuando falta capturar mediciones en el corte."""
    if reporte.sin_medicion == 1:
        return "Falta 1 medición en este corte; cuenta como meta no cumplida."
    if reporte.sin_medicion:
        return (
            f"Faltan {reporte.sin_medicion} mediciones en este corte; "
            "cuentan como metas no cumplidas."
        )
    return ""


def filas_de_metricas(reporte):
    """Filas de «Métricas contra meta»: ID, métrica, tipo, valor en el corte, meta, si cumple,
    valor en el corte anterior y tendencia (RF-16).

    Las dos últimas son «—» si el corte elegido es el primero (no hay con qué comparar).
    """
    comparar = reporte.corte_anterior is not None
    return [
        [
            fila.metrica.clave,
            fila.metrica.nombre,
            fila.metrica.tipo,
            fila.medicion.valor_texto if fila.medicion else "Sin medición",
            fila.metrica.meta_texto,
            "Sí" if fila.cumple else "No",
            (fila.anterior.valor_texto if fila.anterior else "Sin medición") if comparar
            else SIN_DATO,
            (fila.tendencia or "Sin dato") if comparar else SIN_DATO,
        ]
        for fila in reporte.filas
    ]


def texto_comparacion(reporte):
    """La misma frase que la pantalla arriba de la tabla de métricas (RF-16)."""
    if reporte.corte_anterior:
        return reporte.resumen_comparacion
    return "Es el primer corte del proyecto; todavía no hay corte anterior para comparar."


def filas_de_tecnicas(reporte):
    """Filas de «Cumplimiento de técnicas SQA». La evidencia es una lista de (fecha, enlace)."""
    if not reporte.tecnicas:
        return []
    return [
        [
            fila.asignacion.tecnica.nombre,
            str(fila.asignacion.usuario),
            fila.asignacion.frecuencia,
            str(fila.esperadas),
            str(fila.registradas),
            _pct(fila.porcentaje),
            [(aplicacion.fecha.strftime("%d/%m/%Y"), aplicacion.evidencia)
             for aplicacion in fila.aplicaciones],
        ]
        for fila in reporte.tecnicas.tecnicas
    ]


def nombre_archivo(reporte):
    """Nombre del PDF: «reporte-salud-dashboard-sqa-corte-2-2026-10-20.pdf»."""
    proyecto = slugify(reporte.proyecto.nombre) or "proyecto"
    fecha = f"{reporte.corte.fecha:%Y-%m-%d}"
    return f"reporte-salud-{proyecto}-corte-{reporte.numero_corte}-{fecha}.pdf"


# --- Piezas gráficas ---


def _p(texto, estilo="celda"):
    """Párrafo con el texto escapado (los nombres los escribe el usuario)."""
    return Paragraph(escape(str(texto)), ESTILOS[estilo])


def _recortar(texto, fuente, tamano, ancho):
    """Recorta un texto de una línea con «…» para que quepa en el ancho dado."""
    if pdfmetrics.stringWidth(texto, fuente, tamano) <= ancho:
        return texto
    while texto and pdfmetrics.stringWidth(texto + "…", fuente, tamano) > ancho:
        texto = texto[:-1]
    return texto.rstrip() + "…"


def _punto(clase, diametro=7):
    dibujo = Drawing(diametro, diametro)
    dibujo.add(Circle(diametro / 2, diametro / 2, diametro / 2,
                      fillColor=ESTADOS[clase][0], strokeColor=None))
    return dibujo


def _pastilla(texto, clase):
    """Como .pill de sqa.css: fondo claro y texto oscuro del mismo color."""
    _, fondo, tinta = ESTADOS[clase]
    ancho = pdfmetrics.stringWidth(texto, FUENTE_NEGRITA, 7.5) + 14
    dibujo = Drawing(ancho, 12)
    dibujo.add(Rect(0, 0, ancho, 12, rx=6, ry=6, fillColor=fondo, strokeColor=None))
    dibujo.add(String(ancho / 2, 3.4, texto, fontName=FUENTE_NEGRITA, fontSize=7.5,
                      fillColor=tinta, textAnchor="middle"))
    return dibujo


def _anillo(fraccion, clase, texto, diametro=22 * mm):
    """Medidor circular: la parte coloreada es la fracción (0 a 1) y el texto va al centro."""
    dibujo = Drawing(diametro, diametro)
    centro = diametro / 2
    grosor = 3.2 * mm
    radio = centro - 1
    medio = radio - grosor / 2
    dibujo.add(Circle(centro, centro, medio, fillColor=None, strokeColor=GRIS_VACIO,
                      strokeWidth=grosor))
    color = ESTADOS[clase][0]
    if fraccion >= 0.999:
        dibujo.add(Circle(centro, centro, medio, fillColor=None, strokeColor=color,
                          strokeWidth=grosor))
    elif fraccion > 0:
        # Empieza arriba (90°) y avanza en el sentido del reloj.
        dibujo.add(Wedge(centro, centro, radio, 90 - 360 * fraccion, 90,
                         radius1=radio - grosor, fillColor=color, strokeColor=None))
    tamano = 11 if len(texto) <= 5 else 9.5
    dibujo.add(String(centro, centro - tamano * 0.35, texto, fontName=FUENTE_NEGRITA,
                      fontSize=tamano, fillColor=TEXTO, textAnchor="middle"))
    return dibujo


def _barra(porcentaje, ancho):
    """Barra de avance con su porcentaje a la derecha, coloreada como la celda de la pantalla."""
    clase = clase_de_porcentaje(porcentaje)
    largo = ancho - 30
    dibujo = Drawing(ancho, 10)
    dibujo.add(Rect(0, 2.5, largo, 5, rx=2.5, ry=2.5, fillColor=GRIS_VACIO, strokeColor=None))
    if porcentaje:
        relleno = max(largo * min(porcentaje, 100) / 100, 5)
        dibujo.add(Rect(0, 2.5, relleno, 5, rx=2.5, ry=2.5, fillColor=ESTADOS[clase][0],
                        strokeColor=None))
    dibujo.add(String(ancho, 2, _pct(porcentaje), fontName=FUENTE_NEGRITA, fontSize=8,
                      fillColor=ESTADOS[clase][2], textAnchor="end"))
    return dibujo


def _semaforo_dibujo(reporte, ancho, alto):
    """El semáforo de la pantalla: tres luces con la del color encendida, y el color en grande."""
    dibujo = Drawing(ancho, alto)
    cuerpo_x, cuerpo_ancho = 2 * mm, 13 * mm
    dibujo.add(Rect(cuerpo_x, 0, cuerpo_ancho, alto, rx=3 * mm, ry=3 * mm,
                    fillColor=TEXTO_2, strokeColor=None))
    for i, color in enumerate((ROJO, AMARILLO, VERDE)):
        encendida = reporte.semaforo == color
        dibujo.add(Circle(
            cuerpo_x + cuerpo_ancho / 2, alto - (i + 0.5) * alto / 3, 4 * mm,
            fillColor=ESTADOS[CLASE_SEMAFORO[color]][0] if encendida else LUZ_APAGADA,
            strokeColor=None,
        ))
    x = cuerpo_x + cuerpo_ancho + 4 * mm
    libre = ancho - x
    texto = reporte.semaforo.upper()
    tamano = 18
    while tamano > 10 and pdfmetrics.stringWidth(texto, FUENTE_NEGRITA, tamano) > libre:
        tamano -= 1
    dibujo.add(String(x, alto / 2 + 1.5 * mm, texto, fontName=FUENTE_NEGRITA, fontSize=tamano,
                      fillColor=ESTADOS[CLASE_SEMAFORO[reporte.semaforo]][2]))
    dibujo.add(String(x, alto / 2 - 4 * mm, f"Corte {reporte.numero_corte}",
                      fontName=FUENTE_NEGRITA, fontSize=8, fillColor=GRIS_TEXTO))
    dibujo.add(String(x, alto / 2 - 8 * mm, f"{reporte.corte.fecha:%d/%m/%Y}",
                      fontName=FUENTE, fontSize=8, fillColor=GRIS_TEXTO))
    return dibujo


# --- Bloques del reporte ---


def _panel(titulo, cuerpo, ancho, alto):
    """Panel con barra de título turquesa, como «Company Financials» del ejemplo."""
    tabla = Table([[_p(titulo, "panel")], [cuerpo]], colWidths=[ancho], rowHeights=[None, alto])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERDE_SQA),
        ("BOX", (0, 0), (-1, -1), 0.6, VERDE_BORDE),
        ("VALIGN", (0, 1), (-1, 1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tabla


def _puntos_del_diagnostico(reporte):
    """Una línea por cada regla del semáforo, con el punto del color en que está."""
    metas = reporte.porcentaje_metas
    criticos = reporte.defectos_criticos
    tecnicas = reporte.tecnicas
    puntos = [
        (
            _clase_metas(metas),
            f"Metas: {reporte.metas_cumplidas} de {reporte.metas_total} cumplidas ({_pct(metas)})"
            if metas is not None
            else "Metas: el proyecto no tiene métricas asignadas",
        ),
        (
            _clase_defectos(criticos),
            "Defectos críticos (M-03): sin medición en este corte"
            if criticos is None
            else f"Defectos críticos (M-03): {criticos:.0f} abiertos",
        ),
        (
            clase_de_porcentaje(reporte.porcentaje_tecnicas),
            f"Técnicas SQA: {tecnicas.registradas} de {tecnicas.esperadas} aplicaciones "
            f"({_pct(reporte.porcentaje_tecnicas)})"
            if tecnicas and tecnicas.esperadas
            else "Técnicas SQA: todavía no hay aplicaciones esperadas",
        ),
    ]
    aviso = aviso_mediciones_faltantes(reporte)
    if aviso:
        puntos.append(("neutral", aviso))
    return puntos


def _diagnostico(reporte, ancho):
    filas = [
        [_punto(clase), _p(texto, "punto")]
        for clase, texto in _puntos_del_diagnostico(reporte)
    ]
    lista = Table(filas, colWidths=[5 * mm, ancho - 5 * mm])
    lista.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    return [_p(reporte.motivo, "motivo"), Spacer(0, 2.5 * mm), lista]


def _resumen(reporte, ancho):
    """Primera fila: el semáforo y el diagnóstico, lado a lado."""
    alto = 40 * mm
    ancho_semaforo = 62 * mm
    hueco = 4 * mm
    ancho_diagnostico = ancho - ancho_semaforo - hueco
    semaforo = _panel(
        "Semáforo general",
        _semaforo_dibujo(reporte, ancho_semaforo - 16, 32 * mm),
        ancho_semaforo,
        alto,
    )
    diagnostico = _panel(
        "Diagnóstico del corte",
        _diagnostico(reporte, ancho_diagnostico - 16),
        ancho_diagnostico,
        alto,
    )
    return _fila([semaforo, diagnostico], [ancho_semaforo, ancho_diagnostico], hueco)


def _fila(celdas, anchos, hueco):
    """Pone bloques lado a lado con un hueco entre ellos."""
    contenido, columnas = [], []
    for i, (celda, ancho) in enumerate(zip(celdas, anchos)):
        if i:
            contenido.append("")
            columnas.append(hueco)
        contenido.append(celda)
        columnas.append(ancho)
    tabla = Table([contenido], colWidths=columnas)
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tabla


def _tarjetas(reporte, ancho):
    """Segunda fila: los tres indicadores con su medidor circular, como «Key Metrics»."""
    metas, defectos, tecnicas = indicadores(reporte)
    criticos = reporte.defectos_criticos
    medidores = [
        (
            (reporte.porcentaje_metas or 0) / 100,
            _clase_metas(reporte.porcentaje_metas),
            f"Verde desde {METAS_VERDE} % de metas",
        ),
        (
            0 if criticos is None else 1,
            _clase_defectos(criticos),
            "Verde solo con 0 abiertos",
        ),
        (
            min(reporte.porcentaje_tecnicas or 0, 100) / 100,
            clase_de_porcentaje(reporte.porcentaje_tecnicas),
            f"Verde desde {TECNICAS_VERDE} % de aplicaciones",
        ),
    ]
    hueco = 4 * mm
    ancho_tarjeta = (ancho - 2 * hueco) / 3
    tarjetas = []
    for (titulo, valor, ayuda), (fraccion, clase, objetivo) in zip(
        (metas, defectos, tecnicas), medidores
    ):
        textos = [_p(titulo, "k"), Spacer(0, 1 * mm), _p(ayuda or SIN_DATO, "h"),
                  Spacer(0, 2 * mm), _p(objetivo, "objetivo")]
        # Alto fijo para que las tres tarjetas queden parejas.
        tarjeta = Table([[_anillo(fraccion, clase, valor, diametro=20 * mm), textos]],
                        colWidths=[23 * mm, ancho_tarjeta - 23 * mm], rowHeights=[26 * mm])
        tarjeta.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), FONDO_TARJETA),
            ("BOX", (0, 0), (-1, -1), 0.6, VERDE_BORDE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        tarjetas.append(tarjeta)
    return _fila(tarjetas, [ancho_tarjeta] * 3, hueco)


def _titulo_seccion(texto, ancho):
    tabla = Table([[_p(texto, "seccion")]], colWidths=[ancho])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), VERDE_SQA),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, VERDE_OSC),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tabla


def _estilo_tabla(vacia=False, con_total=False):
    comandos = [
        ("BACKGROUND", (0, 0), (-1, 0), VERDE_CLARO),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, VERDE_BORDE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, LINEA),
        ("BOX", (0, 0), (-1, -1), 0.6, VERDE_BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if vacia:
        comandos.append(("SPAN", (0, 1), (-1, 1)))
    if con_total:
        comandos += [
            ("BACKGROUND", (0, -1), (-1, -1), FONDO_TARJETA),
            ("LINEABOVE", (0, -1), (-1, -1), 0.8, VERDE_BORDE),
        ]
    return TableStyle(comandos)


def _valor(valor, negrita=True):
    if valor == "Sin medición":
        return Paragraph(f'<font color="#605e5c" size="7.5">{valor}</font>', ESTILOS["celda"])
    texto = f"<b>{escape(valor)}</b>" if negrita else escape(valor)
    return Paragraph(texto, ESTILOS["celda"])


def _tendencia(texto):
    """Pastilla de la tendencia, con los colores de la pantalla (.pill good, bad o gray)."""
    if texto == "Sin dato":
        return Paragraph(f'<font color="#605e5c">{texto}</font>', ESTILOS["celda"])
    return _pastilla(texto, CLASE_TENDENCIA.get(texto, "gray"))


def _tabla_metricas(reporte, ancho):
    # RF-16: si hay corte anterior, se agregan su valor (antes del actual) y la tendencia.
    comparar = reporte.corte_anterior is not None
    encabezados = ["ID", "Métrica", "Tipo"]
    anchos = [14 * mm, None, 19 * mm]
    if comparar:
        encabezados.append(f"Corte {reporte.numero_corte_anterior}")
        anchos.append(23 * mm)
    encabezados += [f"Corte {reporte.numero_corte}", "Meta", "Cumple"]
    anchos += [23 * mm if comparar else 24 * mm, 19 * mm, 18 * mm]
    if comparar:
        encabezados.append("Tendencia")
        anchos.append(27 * mm)
    anchos[1] = ancho - sum(a for a in anchos if a)

    datos = [[_p(texto, "encabezado") for texto in encabezados]]
    for clave, nombre, tipo, valor, meta, cumple, anterior, tendencia in filas_de_metricas(
        reporte
    ):
        fila = [_p(clave, "clave"), _p(nombre), _p(tipo)]
        if comparar:
            fila.append(_valor(anterior, negrita=False))
        fila += [_valor(valor), _p(meta), _pastilla(cumple, "good" if cumple == "Sí" else "bad")]
        if comparar:
            fila.append(_tendencia(tendencia))
        datos.append(fila)
    vacia = len(datos) == 1
    if vacia:
        datos.append(
            [_p("El proyecto no tiene métricas asignadas.", "h")] + [""] * (len(anchos) - 1)
        )
    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    tabla.setStyle(_estilo_tabla(vacia=vacia))
    return tabla


def _evidencias(evidencias):
    if not evidencias:
        return Paragraph('<font color="#605e5c">Sin evidencia</font>', ESTILOS["celda"])
    enlaces = [
        f'<a href={quoteattr(enlace)} color="{ENLACE}"><u>{fecha}</u></a>'
        for fecha, enlace in evidencias
    ]
    return Paragraph(", ".join(enlaces), ESTILOS["celda"])


def _tabla_tecnicas(reporte, ancho):
    encabezados = [
        "Técnica", "Responsable", "Frecuencia", "Registradas", "Cumplimiento", "Evidencia",
    ]
    # Ninguna columna más angosta que su encabezado (más el relleno), para que no se corte.
    minimos = [26 * mm, 18 * mm, 18 * mm, 32 * mm, 27 * mm]
    anchos = [None] + [
        max(minimo, pdfmetrics.stringWidth(texto, FUENTE_NEGRITA, 8) + 14)
        for texto, minimo in zip(encabezados[1:], minimos)
    ]
    anchos[0] = ancho - sum(anchos[1:])
    ancho_barra = anchos[4] - 12

    datos = [[_p(texto, "encabezado") for texto in encabezados]]
    filas = filas_de_tecnicas(reporte)
    for fila, cumplimiento in zip(filas, reporte.tecnicas.tecnicas if filas else []):
        tecnica, responsable, frecuencia, esperadas, registradas, _, evidencias = fila
        datos.append([
            _p(tecnica),
            _p(responsable),
            _p(frecuencia),
            _p(f"{registradas} de {esperadas}"),
            _barra(cumplimiento.porcentaje, ancho_barra),
            _evidencias(evidencias),
        ])
    if filas:
        tecnicas = reporte.tecnicas
        datos.append([
            _p("Total del proyecto", "clave"), "", "",
            _p(f"{tecnicas.registradas} de {tecnicas.esperadas}", "clave"),
            _barra(reporte.porcentaje_tecnicas, ancho_barra),
            "",
        ])
    else:
        datos.append([_p("El proyecto no tiene técnicas asignadas.", "h")] + [""] * 5)
    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    tabla.setStyle(_estilo_tabla(vacia=not filas, con_total=bool(filas)))
    return tabla


# --- Encabezado y pie de página (se dibujan directo en la hoja) ---


def _chip(lienzo, x, y, texto, maximo):
    texto = _recortar(texto, FUENTE, 7.5, maximo)
    ancho = pdfmetrics.stringWidth(texto, FUENTE, 7.5) + 12
    lienzo.setFillColor(VERDE_OSC)
    lienzo.roundRect(x, y, ancho, 5.2 * mm, 2.6 * mm, stroke=0, fill=1)
    lienzo.setFillColor(colors.white)
    lienzo.drawString(x + 6, y + 1.65 * mm, texto)
    return x + ancho + 2 * mm


def _dibujar_banda(lienzo, reporte, generado):
    """Banda turquesa de lado a lado, como la barra superior del sistema."""
    ancho_hoja, alto_hoja = A4
    abajo = alto_hoja - ALTO_BANDA
    lienzo.setFillColor(VERDE_SQA)
    lienzo.rect(0, abajo, ancho_hoja, ALTO_BANDA, stroke=0, fill=1)
    lienzo.setFillColor(VERDE_OSC)
    lienzo.rect(0, abajo, ancho_hoja, 1.2 * mm, stroke=0, fill=1)

    # Marca «SQA», como .brand-mark
    lado = 13 * mm
    marca_y = alto_hoja - 6 * mm - lado
    lienzo.setFillColor(colors.white)
    lienzo.roundRect(MARGEN, marca_y, lado, lado, 1.5 * mm, stroke=0, fill=1)
    lienzo.setFillColor(VERDE_SQA)
    lienzo.setFont(FUENTE_NEGRITA, 10)
    lienzo.drawCentredString(MARGEN + lado / 2, marca_y + lado / 2 - 3.5, "SQA")

    x = MARGEN + lado + 5 * mm
    derecha = ancho_hoja - MARGEN
    lienzo.setFillColor(colors.white)
    lienzo.setFont(FUENTE_NEGRITA, 17)
    lienzo.drawString(x, alto_hoja - 11.5 * mm, "Reporte de salud")
    lienzo.setFont(FUENTE, 7.5)
    lienzo.drawRightString(derecha, alto_hoja - 8 * mm, f"Generado el {generado}")
    lienzo.setFont(FUENTE, 11)
    proyecto = _recortar(reporte.proyecto.nombre, FUENTE, 11, derecha - x)
    lienzo.drawString(x, alto_hoja - 17.5 * mm, proyecto)

    lienzo.setFont(FUENTE, 7.5)
    chip_y = alto_hoja - 25.5 * mm
    maximo = (derecha - x) / 3 - 2 * mm
    for texto in (
        f"Corte {reporte.numero_corte} · {reporte.corte.fecha:%d/%m/%Y}",
        f"Periodo: {reporte.proyecto.periodo}",
        f"Líder: {reporte.proyecto.lider}",
    ):
        x = _chip(lienzo, x, chip_y, texto, maximo)


def _dibujar_pie(lienzo, numero, texto):
    ancho_hoja = A4[0]
    lienzo.setStrokeColor(VERDE_SQA)
    lienzo.setLineWidth(1)
    lienzo.line(MARGEN, 13 * mm, ancho_hoja - MARGEN, 13 * mm)
    lienzo.setFont(FUENTE, 7.5)
    lienzo.setFillColor(GRIS_TEXTO)
    lienzo.drawString(MARGEN, 9 * mm, _recortar(texto, FUENTE, 7.5, ancho_hoja - 2 * MARGEN - 60))
    lienzo.drawRightString(ancho_hoja - MARGEN, 9 * mm, f"Página {numero}")


def generar_pdf(reporte):
    """RF-17: devuelve el reporte de salud como PDF (bytes)."""
    _registrar_fuentes()
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=A4,
        leftMargin=MARGEN,
        rightMargin=MARGEN,
        topMargin=ALTO_BANDA + 7 * mm,
        bottomMargin=18 * mm,
        title=f"Reporte de salud — {reporte.proyecto.nombre} — Corte {reporte.numero_corte}",
        author="Dashboard SQA",
        subject="Reporte de salud del proyecto (RF-15)",
    )
    ancho = documento.width
    generado = timezone.localtime().strftime("%d/%m/%Y %H:%M")
    pie = (
        f"Dashboard SQA · Reporte de salud de {reporte.proyecto.nombre} · "
        f"Corte {reporte.numero_corte} ({reporte.corte.fecha:%d/%m/%Y})"
    )

    def dibujar_hoja(lienzo, doc):
        lienzo.saveState()
        _dibujar_banda(lienzo, reporte, generado)
        _dibujar_pie(lienzo, doc.page, pie)
        lienzo.restoreState()

    contenido = [
        _resumen(reporte, ancho),
        Spacer(0, 4 * mm),
        _tarjetas(reporte, ancho),
        Spacer(0, 6 * mm),
        _titulo_seccion("Métricas contra meta", ancho),
        Spacer(0, 1.5 * mm),
        _p(texto_comparacion(reporte), "objetivo"),
        Spacer(0, 1.5 * mm),
        _tabla_metricas(reporte, ancho),
        Spacer(0, 6 * mm),
        _titulo_seccion("Cumplimiento de técnicas SQA", ancho),
        Spacer(0, 2 * mm),
        _tabla_tecnicas(reporte, ancho),
        Spacer(0, 2 * mm),
        _p("Cada enlace de evidencia es una aplicación registrada hasta la fecha del corte.", "h"),
        _p(
            "Regla del semáforo: Rojo, Amarillo y Verde, en ese orden; gana la más estricta "
            "que aplique.",
            "h",
        ),
    ]
    documento.build(contenido, onFirstPage=dibujar_hoja, onLaterPages=dibujar_hoja)
    return salida.getvalue()
