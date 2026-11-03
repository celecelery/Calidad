# Casos de prueba — módulos 2, 3 y 4

Tarea 10.2. Casos escritos a partir del **criterio de aceptación** de cada requisito de la Especificación de Requisitos v1.4 (secciones 5 y 8). Son la base de las pruebas automatizadas (tarea 10.3) y de las pruebas manuales.

**Alcance:** RF-05 a RF-15 y RF-20. Se empieza por RF-15, con al menos un caso por cada color del semáforo.

**Tipos:**
- **Unitaria:** prueba una validación o un cálculo por separado.
- **Integración:** recorre varias pantallas como lo haría un usuario.
- **Manual:** la hace una persona en el navegador.

**Columna «Automatizada en»:** archivo y nombre de la prueba de pytest que cubre el caso (`archivo › prueba`, dentro de `archivosPython/dashboard/`). «Por automatizar (10.3)» significa que la prueba se escribe en la tarea 10.3. «Pendiente de implementar» significa que el requisito todavía no está en `main`.

**Datos comunes:** periodo *Ago–Dic 2026* (10/08/2026 – 15/12/2026), proyecto *Dashboard SQA* con las 6 métricas base (M-01 a M-06) y corte del 20/10/2026, salvo que el caso diga otra cosa.

---

## RF-15 — Reporte de salud de un proyecto en un corte

**Criterio de aceptación:** muestra semáforo general, tabla de métricas contra meta y cumplimiento de técnicas.
**Regla del semáforo (sección 8):** se usa la más estricta, empezando por Rojo.
- **Rojo:** M-03 > 0, o menos del 50 % de metas cumplidas, o técnicas por debajo del 60 %.
- **Amarillo:** no es Rojo, y metas entre 50 % y 82 % o técnicas entre 60 % y 79 %.
- **Verde:** al menos 83 % de metas, sin defectos críticos y técnicas en 80 % o más.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-15-01 | Unitaria | Calcular el reporte del corte | 5 de 6 metas cumplidas (83 %), M-03 = 0, técnicas al 100 % | Semáforo **Verde** | `test_reporte_salud.py` › `test_verde_con_5_de_6_metas_sin_criticos_y_tecnicas_al_100` |
| CP-15-02 | Unitaria | Calcular el reporte del corte | 4 de 6 metas (67 %), M-03 = 0, técnicas al 100 % | Semáforo **Amarillo** | `test_reporte_salud.py` › `test_amarillo_con_4_de_6_metas` |
| CP-15-03 | Unitaria | Calcular el semáforo | Metas al 100 %, M-03 = 0, técnicas al 60 % y al 79.9 % | Semáforo **Amarillo** en los dos casos | `test_reporte_salud.py` › `test_amarillo_por_tecnicas_entre_60_y_79` |
| CP-15-04 | Unitaria | Calcular el reporte del corte | Todas las metas cumplidas salvo M-03 = 1 (un defecto crítico abierto), técnicas al 100 % | Semáforo **Rojo**; M-03 se evalúa con sentido «igual o menor» | `test_reporte_salud.py` › `test_rojo_con_un_defecto_critico_respeta_el_sentido_de_m03` |
| CP-15-05 | Unitaria | Calcular el reporte del corte | 2 de 6 metas (33 %), técnicas bajas | Semáforo **Rojo** | `test_reporte_salud.py` › `test_rojo_con_2_de_6_metas_y_tecnicas_bajas` |
| CP-15-06 | Unitaria | Calcular el semáforo | Metas al 100 %, M-03 = 0, técnicas al 59.9 % | Semáforo **Rojo** | `test_reporte_salud.py` › `test_rojo_por_tecnicas_menores_a_60` |
| CP-15-07 | Unitaria | Calcular el semáforo en los límites | Metas 49.9 / 50 / 82.9 / 83 %; técnicas 59.9 / 60 / 79.9 / 80 % | 49.9 % → Rojo; 50 % y 82.9 % → Amarillo; 83 % → Verde. Técnicas: 59.9 % → Rojo; 60 % y 79.9 % → Amarillo; 80 % → Verde | `test_reporte_salud.py` › `test_rojo_por_menos_del_50_por_ciento_de_metas`, `test_amarillo_por_metas_entre_50_y_82`, `test_limites_del_verde`, `test_metas_de_6_metricas` |
| CP-15-08 | Unitaria | Calcular el semáforo | Metas al 66 % (Amarillo) y técnicas al 50 % (Rojo) a la vez | Gana la regla más estricta: **Rojo** | `test_reporte_salud.py` › `test_rojo_gana_aunque_tambien_aplique_amarillo` |
| CP-15-09 | Unitaria | Calcular el reporte de un corte con una métrica sin capturar | 5 métricas capturadas que cumplen y 1 sin medición | La métrica sin medición cuenta como **no cumplida** y el reporte dice cuántas faltan | `test_reporte_salud.py` › `test_medicion_faltante_cuenta_como_meta_no_cumplida` |
| CP-15-10 | Unitaria | Calcular el semáforo con datos inexistentes | (a) sin aplicaciones de técnicas esperadas; (b) sin medición de M-03; (c) sin métricas asignadas; (d) metas al 40 % sin M-03 ni técnicas | (a), (b) y (c): como máximo **Amarillo**, nunca Verde; (d): sigue en **Rojo** | `test_reporte_salud.py` › `test_sin_tecnicas_esperadas_no_puede_ser_verde`, `test_sin_medicion_de_defectos_no_puede_ser_verde`, `test_sin_metricas_no_puede_ser_verde`, `test_dato_inexistente_no_quita_el_rojo` |
| CP-15-11 | Integración | Abrir Proyectos › proyecto › Reporte de salud | Proyecto con mediciones y una técnica con evidencia | La pantalla muestra el semáforo, la tabla de métricas (valor, meta y si cumple) y las técnicas con su porcentaje y enlaces de evidencia | `test_reporte_salud.py` › `test_tabla_de_metricas_con_valor_meta_y_si_cumple`, `test_tecnicas_con_enlaces_de_evidencia` |
| CP-15-12 | Integración | Elegir un corte anterior en el selector del reporte | Corte 1 con valores que no cumplen; corte 2 con valores que sí | El reporte usa solo las mediciones y aplicaciones hasta la fecha del corte elegido | `test_reporte_salud.py` › `test_usa_las_mediciones_del_corte_elegido`, `test_elegir_otro_corte` |
| CP-15-13 | Integración | Abrir el reporte de un proyecto sin cortes | Proyecto recién registrado | Aviso de que no hay cortes; no se muestra semáforo | `test_reporte_salud.py` › `test_sin_cortes_avisa` |

## Flujo completo — registrar proyecto → capturar medición → generar reporte

Recorre los módulos 1 a 4 por las pantallas, con el cliente de pruebas de Django. Un caso por cada color del semáforo.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-INT-01 | Integración | 1. Registrar el periodo. 2. Registrar el proyecto. 3. Agregar un corte. 4. Capturar M-01 a M-06. 5. Asignar «Revisión de pares» por corte. 6. Registrar su aplicación con evidencia. 7. Abrir el reporte | M-01 = 80, M-02 = 97, M-03 = 0, M-04 = 92, M-05 = 100, M-06 = 95; aplicación del 15/10/2026 con enlace a un PR | Cada paso redirige sin errores; el reporte muestra 6 de 6 metas, técnicas al 100 % y semáforo **Verde** | Por automatizar (10.3) |
| CP-INT-02 | Integración | Igual que CP-INT-01 | M-01 = 60 y M-04 = 85 (no cumplen); las demás cumplen | 4 de 6 metas y semáforo **Amarillo** | Por automatizar (10.3) |
| CP-INT-03 | Integración | Igual que CP-INT-01 | M-03 = 1; las demás cumplen | Semáforo **Rojo** por el defecto crítico | Por automatizar (10.3) |
| CP-INT-04 | Integración | Igual que CP-INT-01, pero con dos cortes (15/09 y 20/10) y una sola aplicación | Técnica por corte: 1 de 2 aplicaciones (50 %) | Semáforo **Rojo** por técnicas debajo del 60 % | Por automatizar (10.3) |
| CP-INT-05 | Integración | Capturar M-01 con un valor fuera de rango y luego abrir el reporte | M-01 = 105 % | La captura se rechaza con «Fuera de rango: un porcentaje va de 0 a 100.» y el reporte cuenta M-01 como medición faltante | Por automatizar (10.3) |
| CP-INT-06 | Integración | Capturar las 6 métricas y abrir el reporte; corregir M-01 en el mismo corte y volver a abrirlo | M-01 = 60 y M-04 = 85 (no cumplen); después M-01 = 75; técnicas al 100 % | Primero 4 de 6 metas y **Amarillo**; después de corregir, 5 de 6 y **Verde**. El valor corregido reemplaza al anterior | Por automatizar (10.3) |

## RF-14 — Porcentaje de cumplimiento de técnicas

**Criterio de aceptación:** porcentaje = aplicaciones registradas / aplicaciones esperadas en el periodo.
- **Esperadas:** por corte, una por cada corte hasta el evaluado; por PR, los PRs fusionados acumulados al corte; única, 1.
- **Más aplicaciones de las esperadas:** la técnica cuenta como 100 %.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-14-01 | Unitaria | Calcular las esperadas | Técnica «Por corte», proyecto con 3 cortes | 3 esperadas | `test_aplicaciones.py` › `test_por_corte_espera_una_por_corte` |
| CP-14-02 | Unitaria | Calcular las esperadas | Técnica «Por PR», 8 PRs fusionados al último corte | 8 esperadas | `test_aplicaciones.py` › `test_por_pr_espera_los_prs_fusionados_al_ultimo_corte` |
| CP-14-03 | Unitaria | Calcular las esperadas | Técnica «Única» | 1 esperada | `test_aplicaciones.py` › `test_unica_espera_una` |
| CP-14-04 | Unitaria | Calcular el porcentaje del proyecto | 5 técnicas con 14 aplicaciones registradas de 18 esperadas (ejemplo del mockup) | 78 % | `test_aplicaciones.py` › `test_ejemplo_del_mockup_14_de_18_es_78` |
| CP-14-05 | Unitaria | Calcular el porcentaje | Técnica con 5 aplicaciones de 3 esperadas, junto a otra atrasada | Cuenta como 100 %; el excedente no compensa a la atrasada | `test_aplicaciones.py` › `test_mas_aplicaciones_que_las_esperadas_cuenta_como_100` |
| CP-14-06 | Unitaria | Calcular el porcentaje | Proyecto sin técnicas o técnica «Por PR» sin PRs | No hay porcentaje (no entra al total) | `test_aplicaciones.py` › `test_sin_esperadas_no_hay_porcentaje`, `test_tecnica_sin_esperadas_no_entra_en_el_total` |
| CP-14-07 | Unitaria | Calcular el cumplimiento en un corte anterior | Aplicaciones antes y después de la fecha del corte | Solo cuentan los cortes y las aplicaciones hasta esa fecha | `test_aplicaciones.py` › `test_en_un_corte_solo_cuentan_los_cortes_hasta_esa_fecha`, `test_en_un_corte_solo_cuentan_las_aplicaciones_hasta_esa_fecha` |

## RF-13 — Registrar la aplicación de una técnica

**Criterio de aceptación:** no se guarda sin enlace de evidencia.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-13-01 | Integración | Técnicas SQA › Registrar › llenar y guardar | Fecha 15/10/2026, resultado Favorable, evidencia `https://github.com/celecelery/Calidad/pull/14` | Se guarda, regresa a Técnicas SQA y el registro cuenta para el cumplimiento | `test_aplicaciones.py` › `test_post_valido_guarda_y_regresa_a_tecnicas` |
| CP-13-02 | Unitaria | Guardar sin enlace | Evidencia vacía | No se guarda; pide el enlace de evidencia | `test_aplicaciones.py` › `test_sin_enlace_de_evidencia_no_se_guarda`, `test_post_sin_evidencia_no_guarda_y_lo_dice` |
| CP-13-03 | Unitaria | Guardar con un enlace no válido | `acta del lunes`, `ftp://servidor/acta` | Se rechaza: debe empezar con `https://` o `http://` | `test_aplicaciones.py` › `test_evidencia_que_no_es_enlace_se_rechaza`, `test_evidencia_solo_acepta_http_y_https` |
| CP-13-04 | Unitaria | Guardar con fecha inválida | Fecha fuera del periodo; fecha futura | Se rechaza con el mensaje correspondiente | `test_aplicaciones.py` › `test_fecha_fuera_del_periodo_se_rechaza`, `test_fecha_futura_se_rechaza` |

## RF-12 — Asignar técnicas a un proyecto

**Criterio de aceptación:** cada asignación tiene responsable y frecuencia.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-12-01 | Integración | Técnicas SQA › Asignar técnica | «Revisión de pares», responsable, frecuencia «Por corte» | Se crea la asignación solo en ese proyecto | `test_tecnicas.py` › `test_post_valido_crea_la_asignacion_en_ese_proyecto` |
| CP-12-02 | Unitaria | Asignar sin responsable o sin frecuencia | Responsable vacío; frecuencia vacía o inventada | Se rechaza | `test_tecnicas.py` › `test_sin_responsable_se_rechaza`, `test_sin_frecuencia_se_rechaza`, `test_frecuencia_fuera_de_las_opciones_se_rechaza` |
| CP-12-03 | Unitaria | Asignar dos veces la misma técnica | «Revisión de pares» ya asignada | Se rechaza en el proyecto, pero se acepta en otro | `test_tecnicas.py` › `test_misma_tecnica_dos_veces_en_el_proyecto_se_rechaza`, `test_misma_tecnica_en_otro_proyecto_se_acepta` |

## RF-11 — Catálogo de técnicas SQA

**Criterio de aceptación:** el sistema incluye precargadas al menos 8 técnicas.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-11-01 | Unitaria | Consultar el catálogo en una base nueva | Migraciones aplicadas | Al menos 8 técnicas precargadas, todas con descripción | `test_tecnicas.py` › `test_hay_al_menos_8_tecnicas_precargadas`, `test_todas_tienen_descripcion` |
| CP-11-02 | Integración | Catálogos › Técnicas SQA › Nueva técnica sin descripción | Solo nombre | No se guarda; marca el campo en rojo | `test_tecnicas.py` › `test_post_sin_descripcion_no_guarda` |
| CP-11-03 | Unitaria | Registrar una técnica con nombre repetido | `revisión DE PARES` | Se rechaza sin importar mayúsculas | `test_tecnicas.py` › `test_nombre_repetido_sin_importar_mayusculas_se_rechaza` |

## RF-10 — Resumen de proyectos activos en el dashboard

**Criterio de aceptación:** cada proyecto aparece con su semáforo actual.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-10-01 | Integración | Abrir Inicio | Tres proyectos activos: uno Verde, uno Amarillo y uno Rojo en su último corte | Cada proyecto aparece con su semáforo actual, igual al de su reporte de salud | Pendiente de implementar (tarea 7.3) |
| CP-10-02 | Integración | Archivar un proyecto y abrir Inicio | Un proyecto archivado | El archivado no aparece en el dashboard | Pendiente de implementar (tarea 7.3) |
| CP-10-03 | Manual | Abrir Inicio con 20 proyectos registrados y cronometrar | 20 proyectos con cortes | Carga en menos de 3 s (RNF-01) | Pendiente de implementar (tarea 7.3) |

## RF-09 — Gráfica de evolución contra la meta

**Criterio de aceptación:** la gráfica muestra la línea de meta y un punto por corte.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-09-01 | Integración | Proyecto › Evolución › elegir M-01 | Tres cortes con M-01 = 58, 65 y 72 % | Una línea de meta en 70 % y tres puntos, uno por corte | Pendiente de implementar (tarea 7.3) |
| CP-09-02 | Integración | Elegir una métrica con un corte sin medición | Corte 2 sin valor | El corte sin medición no dibuja punto | Pendiente de implementar (tarea 7.3) |

## RF-08 — Capturar la medición de una métrica en un corte

**Criterio de aceptación:** no se acepta un valor fuera del rango de la unidad (por ejemplo, porcentaje mayor a 100).

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-08-01 | Unitaria | Validar un porcentaje en los límites | 0, 72.5 y 100 | Se aceptan | `test_mediciones.py` › `test_limites_del_porcentaje_se_aceptan`, `test_porcentaje_valido_se_acepta` |
| CP-08-02 | Unitaria | Validar un porcentaje mayor a 100 | 105 | Se rechaza: «Fuera de rango: un porcentaje va de 0 a 100.» | `test_mediciones.py` › `test_porcentaje_mayor_a_100_se_rechaza` |
| CP-08-03 | Unitaria | Validar un porcentaje negativo | -1 | Se rechaza con el mismo mensaje | `test_mediciones.py` › `test_porcentaje_negativo_se_rechaza` |
| CP-08-04 | Unitaria | Validar un conteo | -2; 1.5; 150 | -2 y 1.5 se rechazan (negativo, no entero); 150 se acepta | `test_mediciones.py` › `test_conteo_negativo_se_rechaza`, `test_conteo_con_decimales_se_rechaza`, `test_conteo_mayor_a_100_se_acepta` |
| CP-08-05 | Integración | Capturar dos veces la misma métrica en el mismo corte | M-01 = 65 y luego 72 | Queda un solo valor: 72 | `test_mediciones.py` › `test_capturar_otra_vez_corrige_el_valor` |
| CP-08-06 | Integración | Capturar un valor fuera de rango en la pantalla | M-01 = 105 | No se guarda; el error aparece junto al campo y conserva lo escrito | `test_mediciones.py` › `test_valor_fuera_de_rango_no_se_guarda_y_muestra_el_error` |
| CP-08-07 | Unitaria | Agregar un corte fuera del periodo o repetido | 16/12/2026; 20/10/2026 repetido | Se rechazan | `test_mediciones.py` › `test_fecha_fuera_del_periodo_se_rechaza`, `test_fecha_repetida_se_rechaza` |

## RF-07 — Asignar métricas a un proyecto

**Criterio de aceptación:** un proyecto nuevo recibe las 6 métricas base por defecto.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-07-01 | Integración | Registrar un proyecto desde el formulario | Proyecto *App de inventario* | Tiene asignadas M-01 a M-06 | `test_metricas.py` › `test_proyecto_registrado_desde_el_formulario_recibe_las_metricas_base` |
| CP-07-02 | Integración | Quitar las métricas de un proyecto | Dos proyectos; se quitan todas en uno | El otro conserva sus 6 métricas | `test_metricas.py` › `test_quitar_no_afecta_a_otros_proyectos` |
| CP-07-03 | Integración | Asignar una métrica que ya tiene | M-01 | Se rechaza: «Selecciona una métrica del catálogo que no esté asignada.» | `test_metricas.py` › `test_metrica_ya_asignada_se_rechaza` |

## RF-06 — Catálogo de métricas

**Criterio de aceptación:** una métrica no se guarda sin meta ni tipo.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-06-01 | Unitaria | Guardar una métrica sin meta | Meta vacía | No se guarda; «Este campo es obligatorio.» | `test_metricas.py` › `test_sin_meta_no_se_guarda` |
| CP-06-02 | Unitaria | Guardar una métrica sin tipo | Tipo vacío | No se guarda; «Este campo es obligatorio.» | `test_metricas.py` › `test_sin_tipo_no_se_guarda` |
| CP-06-03 | Integración | Catálogos › Métricas › Nueva métrica completa | M-07 *Densidad de defectos*, conteo, meta ≤ 2 | Se guarda con su sentido y no es métrica base | `test_metricas.py` › `test_post_valido_registra_la_metrica` |
| CP-06-04 | Unitaria | Guardar una meta de porcentaje mayor a 100 | Unidad %, meta 105 | Se rechaza por fuera de rango | `test_metricas.py` › `test_porcentaje_mayor_a_100_se_rechaza` |

## RF-05 — Archivar un proyecto

**Criterio de aceptación:** el proyecto archivado no aparece en el dashboard pero sí en el historial; un proyecto archivado se puede reactivar.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-05-01 | Integración | Proyecto › Datos › Archivar | Proyecto con mediciones | No se borra el proyecto ni sus datos | `test_archivar.py` › `test_archivar_no_borra_el_proyecto_ni_sus_datos` |
| CP-05-02 | Integración | Archivar y revisar el menú y la lista | Proyecto archivado | Sale del menú lateral, pero sigue en Proyectos y en el filtro por estado | `test_archivar.py` › `test_archivado_sale_del_menu_lateral`, `test_archivado_sigue_en_la_lista_y_en_el_filtro_por_estado` |
| CP-05-03 | Integración | Reactivar un archivado | Proyecto archivado | Vuelve a Activo y regresa al menú | `test_archivar.py` › `test_reactivar_lo_devuelve_al_menu` |
| CP-05-04 | Integración | Archivar por GET (sin el botón) | URL directa | No archiva (solo acepta POST) | `test_archivar.py` › `test_archivar_solo_acepta_post` |

## RF-20 — Perfiles Administrador y Miembro

**Criterio de aceptación:** un Miembro no puede editar catálogos.

| ID | Tipo | Pasos | Datos | Resultado esperado | Automatizada en |
|---|---|---|---|---|---|
| CP-20-01 | Integración | Como Miembro, entrar a Catálogos › Métricas y guardar una métrica | Usuario con perfil Miembro | No puede crear ni editar: acceso denegado o sin botón de guardar | Pendiente de implementar (tarea 6.5) |
| CP-20-02 | Integración | Como Miembro, crear o editar una técnica o un periodo | Usuario con perfil Miembro | Acceso denegado | Pendiente de implementar (tarea 6.5) |
| CP-20-03 | Integración | Como Miembro, capturar una medición y registrar una aplicación | Usuario con perfil Miembro | Sí puede (la captura es del Miembro) | Pendiente de implementar (tarea 6.5) |
| CP-20-04 | Integración | Como Administrador, editar catálogos y periodos | Usuario con perfil Administrador | Sí puede | Pendiente de implementar (tarea 6.5) |
| CP-20-05 | Integración | Registrar un proyecto en una base nueva | Solo usuarios registrados con la app | La lista «Líder» ofrece a los usuarios registrados (defecto reportado al probar RF-08) | Pendiente de implementar (tarea 6.5) |

## Resumen

| Requisito | Casos | Automatizados | Por automatizar (10.3) | Pendientes de implementar |
|---|---|---|---|---|
| RF-15 | 13 | 13 | 0 | 0 |
| Flujo completo | 6 | 0 | 6 | 0 |
| RF-14 | 7 | 7 | 0 | 0 |
| RF-13 | 4 | 4 | 0 | 0 |
| RF-12 | 3 | 3 | 0 | 0 |
| RF-11 | 3 | 3 | 0 | 0 |
| RF-10 | 3 | 0 | 0 | 3 |
| RF-09 | 2 | 0 | 0 | 2 |
| RF-08 | 7 | 7 | 0 | 0 |
| RF-07 | 3 | 3 | 0 | 0 |
| RF-06 | 4 | 4 | 0 | 0 |
| RF-05 | 4 | 4 | 0 | 0 |
| RF-20 | 5 | 0 | 0 | 5 |
| **Total** | **64** | **48** | **6** | **10** |
