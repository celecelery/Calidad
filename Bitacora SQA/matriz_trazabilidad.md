# Matriz de trazabilidad

Relaciona cada requisito de la Especificación de Requisitos v1.4 con su issue, el PR que lo implementa, sus casos de prueba (`casos_de_prueba.md`, tarea 10.2) y las pruebas automatizadas que lo verifican.
Se actualiza en cada PR que implementa o cambia un requisito.

**Estados:** Pendiente · En progreso · Implementado (fusionado en main con pruebas en verde) · Verificado (además pasó la revisión de QA)

**Última actualización:** 19/11/2026 — tarea 11.6: cierre del sprint 3. Se revisaron los PR #24 a #30 (bitácora #12 a #15), las pruebas no funcionales de la tarea 10.4 y los defectos contra `main` (`5fecfb2`). RF-16, RF-17 y RF-18 quedan Implementado. Los defectos D-01 a D-06 siguen presentes; D-07 a D-10 y D-15 son fallos de CI ya resueltos. Se registraron D-16 a D-31 (hallazgos del modelo de datos, de la tarea 10.4, de proceso y de la revisión de documentos; D-26 a D-28 estaban en el Reporte final como «Sin ID»). El repositorio sigue sin issues (0 abiertos y 0 cerrados): la columna **Issue** dice «Sin issue» o «Por abrir» hasta que se creen con `issues_para_github.md`.

**Actualización anterior:** 05/11/2026 — tarea 11.4: revisión de QA del sprint 2 (bitácora #7 a #11). RF-05 a RF-07 y RF-11 a RF-15 pasan a Verificado.

## Requisitos funcionales

| ID | Requisito | Check-in | Issue | PR | Casos (10.2) | Prueba | Estado |
|---|---|---|---|---|---|---|---|
| RF-01 | Registrar un periodo; no se guarda si la fecha de fin es anterior a la de inicio | 20 oct | Sin issue (por crear) | #9 | — | `dashboard/test_formularios.py`: `PeriodoFormTests`, `VistasFormulariosTests.test_post_periodo_*` | Verificado |
| RF-02 | Registrar un proyecto; nombre y periodo obligatorios, nombre único por periodo | 20 oct | Sin issue (por crear) | #9, #10 | — | `dashboard/test_formularios.py`: `ProyectoFormTests`, `VistasFormulariosTests.test_post_proyecto_*`; `dashboard/test_modelos.py` | Verificado |
| RF-03 | Editar los datos de un proyecto sin afectar a otros | 20 oct | Sin issue (por crear) | #11 | — | `dashboard/test_proyectos.py`: `EditarProyectoTests` | Verificado |
| RF-04 | Listar proyectos filtrando por periodo y estado | 20 oct | Sin issue (por crear) | #11 | — | `dashboard/test_proyectos.py`: `ListaProyectosTests` | Verificado |
| RF-05 | Archivar un proyecto sin borrarlo; se puede reactivar | 3 nov | Por crear (#17 dice `Closes #18`, que es un PR) | #17 | CP-05-01 a CP-05-04 | `dashboard/test_archivar.py`: `ModeloArchivarTests`, `VistaArchivarTests`, `VistaReactivarTests`, `PantallasArchivarTests` | Verificado (bitácora #7 y #9). Pendiente de CP-10-02: Inicio todavía lista los archivados (D-01) |
| RF-06 | Administrar el catálogo de métricas | 3 nov | Por crear | #13 | CP-06-01 a CP-06-04 | `dashboard/test_metricas.py`: `MetricaFormTests`, `CatalogoVistasTests`, `MetaTextoTests`, `CumpleMetaTests` | Verificado (bitácora #7 y #9). Quién puede editarlo depende de RF-20 (D-03) |
| RF-07 | Asignar las 6 métricas base a un proyecto nuevo | 3 nov | Por crear | #13 | CP-07-01 a CP-07-03 | `dashboard/test_metricas.py`: `MetricasBaseTests`, `AsignacionMetricasTests`; prueba interna (bitácora #10) | Verificado (bitácora #7, #9 y #10) |
| RF-08 | Capturar la medición de una métrica en un corte | 3 nov | Por crear; defecto D-05 por abrir | #14 | CP-08-01 a CP-08-07 | `dashboard/test_mediciones.py`: `MedicionFormTests`, `CorteFormTests`, `CapturarMedicionVistaTests`, `AgregarCorteVistaTests`, `TablaMedicionesTests`; prueba interna (bitácora #10) | Implementado (no pasa a Verificado hasta cerrar D-05: error 500 con una medición sin `capturado_por`) |
| RF-09 | Graficar la evolución de cada métrica contra su meta | 3 nov | Defecto D-02 por abrir | #22 | CP-09-01, CP-09-02 | Sin pruebas: `grafica_metricas` (`views.py` 517–545) sin pruebas de la vista | En progreso (#22 fusionado el 04/11; la página sale en blanco y la pestaña Evolución sigue deshabilitada, D-02) |
| RF-10 | Resumen de proyectos activos con semáforo en el dashboard | 3 nov | Defecto D-01 por abrir | #22 | CP-10-01 a CP-10-03 | Sin pruebas de CP-10; `salud.semaforo_actual` ya tiene pruebas en `test_reporte_salud.py` | En progreso (#22 fusionado el 04/11; Inicio no muestra el semáforo y lista los archivados, D-01) |
| RF-11 | Catálogo de técnicas SQA (al menos 8 precargadas) | 3 nov | Por crear | #16 (#15 cerrado sin fusionar) | CP-11-01 a CP-11-03 | `dashboard/test_tecnicas.py`: `CatalogoPrecargadoTests`, `TecnicaSQAFormTests`, `CatalogoVistasTests`; prueba interna (bitácora #10) | Verificado (bitácora #7, #9 y #10). 9 técnicas precargadas |
| RF-12 | Asignar técnicas a un proyecto con responsable y frecuencia | 3 nov | Por crear | #16 (#15 cerrado sin fusionar) | CP-12-01 a CP-12-03 | `dashboard/test_tecnicas.py`: `AsignacionTecnicaFormTests`, `TecnicasProyectoVistaTests`; prueba interna (bitácora #10) | Verificado (bitácora #7, #9 y #10) |
| RF-13 | Registrar la aplicación de una técnica con evidencia | 3 nov | Por crear (#17 dice `Closes #18`, que es un PR) | #17 | CP-13-01 a CP-13-04 | `dashboard/test_aplicaciones.py`: `AplicacionFormTests`, `RegistrarAplicacionVistaTests`; prueba interna (bitácora #10) | Verificado (bitácora #7, #9 y #10) |
| RF-14 | Calcular el porcentaje de cumplimiento de técnicas | 3 nov | Por crear (#17 dice `Closes #18`, que es un PR) | #17, #21 | CP-14-01 a CP-14-07 | `dashboard/test_aplicaciones.py`: `EsperadasTests`, `PorcentajeTests`, `PestanaTecnicasCumplimientoTests`, `PrsFusionadosTests`; `dashboard/test_calculos.py`: `EsperadasFrecuenciaTests`; prueba interna (bitácora #10) | Verificado (bitácora #7, #9 y #10) |
| RF-15 | Generar el reporte de salud de un proyecto en un corte | 3 nov | Por crear (#17 dice `Closes #18`, que es un PR) | #17, #21 | CP-15-01 a CP-15-13; flujo completo CP-INT-01 a CP-INT-06 | `dashboard/test_reporte_salud.py`: `CalcularSemaforoTests`, `ReporteDeSaludTests`, `ReporteVistaTests`; `dashboard/test_calculos.py`: `MotivoDelSemaforoTests`; flujo completo en `dashboard/test_integracion.py`: `FlujoCompletoTests` (tarea 10.3); reporte del corte del 04/11 del propio proyecto (bitácora #11) | Verificado (bitácora #7, #9, #10 y #11) |
| RF-16 | Comparar el reporte con el corte anterior | 19 nov | Sin issue | #28; corrección #30 (fusionado el 19/11) | CP-16-01 a CP-16-07 | `dashboard/test_comparacion.py`: `TendenciaTests`, `ComparacionDelReporteTests`, `ComparacionEnPantallaTests` | Implementado. #28 la dejó en una página aparte que daba error 500 (faltaba `{% load plotly_dash %}`), sin enlace, siempre con los dos últimos cortes y sin pruebas; #30 la puso dentro del reporte de salud, contra el corte anterior al elegido, y agregó las pruebas |
| RF-17 | Exportar el reporte a PDF | 19 nov | Sin issue | #24; la comparación en el PDF llega con #30 | CP-17-01 a CP-17-07 | `dashboard/test_reporte_pdf.py`: `ContenidoDelPdfTests`, `GenerarPdfTests`, `ExportarPdfVistaTests` (respuesta `application/pdf` que empieza con `%PDF-`), `BotonExportarTests` | Implementado (el PDF incluye la comparación desde #30). Se usó ReportLab en lugar de WeasyPrint: falta actualizar el SDS y el documento de Arquitectura (tarea 4.8) |
| RF-18 | Historial de reportes de un proyecto | 19 nov | Sin issue | #29 | — | `dashboard/test_historial.py`: `HistorialDeSaludTests`, `HistorialVistaTests` | Implementado |
| RF-19 | Iniciar y cerrar sesión; sin sesión se redirige al login | 20 oct | Sin issue (por crear) | #7 | — | `cuentas/tests.py`; `dashboard/tests.py`: `InicioTests` | Verificado |
| RF-20 | Perfiles Administrador y Miembro; un Miembro no puede editar catálogos | 3 nov | Defectos D-03, D-04 y D-06 por abrir | #19 (parcial) | CP-20-01 a CP-20-05 | `dashboard/test_proyectos.py`: `PermisosEditarProyectoTests` (solo editar proyecto). Sin pruebas de CP-20-01 a CP-20-05 | En progreso (#19 limita los perfiles y protege editar proyecto, quitar métrica y editar técnica; un Miembro todavía crea y edita métricas, técnicas y periodos, D-03, y no hay forma de dar perfil, D-04) |

## Requisitos no funcionales

| ID | Requisito | Verificación | Issue | PR | Prueba / evidencia | Estado |
|---|---|---|---|---|---|---|
| RNF-01 | El dashboard carga en menos de 3 s con 20 proyectos | Prueba cronometrada en la beta | Sin issue | #31 (prueba `test_rendimiento.py`, en revisión) | Tarea 10.4: 20 proyectos con 3 cortes cada uno; Inicio 0.762 s, lista de proyectos 0.161 s, reporte de salud 0.091 s e historial 0.088 s; todas con HTTP 200 | Passed (medido con la base de pruebas; repetir en el servidor de la demo) |
| RNF-02 | Un usuario nuevo registra un proyecto en menos de 2 min | Prueba con un compañero ajeno al equipo | Sin issue | — | Tarea 10.4: no se pudo medir sin una persona ajena al equipo | Pendiente (depende de un probador externo) |
| RNF-03 | Contraseñas con hash de Django; ninguna credencial en el repositorio | Revisión de código y uso de `.env` | Sin issue | #7 (hash); `.env.example` en el commit `e50b91f` (directo a main antes de proteger la rama); se borró en `8ebed95` y se restauró en la tarea 13.2 (#26). El archivo `.env` nunca se subió | `cuentas/tests.py::test_contrasena_guardada_con_hash` aprobada (tarea 10.4); revisión del historial (bitácora #6 y #13) | Passed con observación (defectos D-21 y D-22): `docker-compose.yml` y otros archivos versionados traen `mypassword` como contraseña por omisión de la base, y la `SECRET_KEY` anterior sigue en el historial (commit `670a646`); conviene cambiarlas antes de un despliegue real |
| RNF-04 | Los formularios validan en el servidor | Pruebas unitarias de formularios | Sin issue | #9, #11, #13, #14, #16, #17 | `dashboard/test_formularios.py`, `dashboard/test_proyectos.py`, `test_metricas.py`, `test_mediciones.py`, `test_tecnicas.py`, `test_aplicaciones.py` (envían datos inválidos por POST; las plantillas usan `novalidate`) | Passed en la tarea 10.4: 220 pruebas de validación aprobadas; las plantillas usan `novalidate` en 8 formularios para que valide el servidor. Verificado para RF-01 a RF-03, RF-06 a RF-08 y RF-11 a RF-13 |
| RNF-05 | Ruff sin errores y pruebas automatizadas en cada módulo | GitHub Actions en cada PR | Defectos D-06 a D-10, D-15, D-18 y D-30 por abrir | #3, #4 (`ci.yml`) | Check «Ruff, pruebas y cobertura» requerido en main; `main` en `5fecfb2` (CI #82 y Reporte final): 349 pruebas aprobadas, cobertura 98.14 %, ruff sin errores (meta 70 %). La corrida local de la tarea 10.4 dio 334 pruebas y 95.59 % porque la copia no tenía los PR #29 y #30 (D-30). Corridas de CI con fallo: 17 de 83 | Passed con observación: las apps `proyectos`, `metricas`, `tecnicas` y `reportes` siguen vacías (sin código ni pruebas); RF-09 y RF-10 sin pruebas (D-01, D-02) |
| RNF-06 | Funciona en Chrome, Firefox y Edge actuales | Prueba manual antes de la entrega final | Sin issue | — | Tarea 10.4: no se ejecutó; Firefox no está instalado en el equipo de QA | Pendiente |
| RNF-07 | Se instala siguiendo solo el README | Un integrante instala desde cero | — | Por crear (rama `docs/13.2-readme-instalacion`) | Tarea 13.2: `README.md` con requisitos, instalación en Windows y Linux (entorno virtual, dependencias, `.env`, base PostgreSQL con Docker, migraciones, superusuario con perfil y servidor), pruebas con ruff y cobertura, despliegue con Docker (tarea 12.1) y estructura del proyecto; restaura `.env.example`, borrado de main en `8ebed95`. Ensayo en una copia limpia el 18/11/2026, cuando la base todavía era SQLite: instalación, migraciones, primer Administrador, inicio de sesión y lista «Líder» correctos; 303 pruebas, ruff sin errores, cobertura 98 % | En progreso. En la tarea 10.4 el entorno virtual existente no tenía el controlador de PostgreSQL (`Error loading psycopg2 or psycopg module`) hasta correr `pip install -r requirements.txt`; falta repetir la instalación desde cero con PostgreSQL y que un integrante la haga en su computadora |

## Resumen del sprint 1

- Requisitos del check-in del 20 de octubre: RF-01, RF-02, RF-03, RF-04 y RF-19. Los 5 están verificados.
- Ningún requisito tiene issue. Al crearlos, cambia "Sin issue (por crear)" por el número y edita el PR para agregar `Closes #número`.
- Pruebas en main al cierre: 51 aprobadas, ruff sin errores y cobertura del 98%.


## Resumen del sprint 2

- Requisitos del check-in del 3 de noviembre: RF-05 a RF-15 y RF-20.
- **Verificados (8):** RF-05, RF-06, RF-07, RF-11, RF-12, RF-13, RF-14 y RF-15.
- **Implementado con defecto abierto (1):** RF-08 (D-05).
- **En progreso (3):** RF-09 y RF-10 (PR #22, fusionado el 04/11; D-01 y D-02) y RF-20 (PR #19, parcial; D-03 y D-04).
- Ningún requisito tiene issue: el repositorio no tiene issues (del #1 al #22 son PR). `Closes #18` (#17) y `Closes #19` (#18) apuntan a PRs.
- Pruebas en main al corte del 04/11: 303 aprobadas, ruff sin errores y cobertura del 98 %. Casos de prueba: 64, de los cuales 54 están automatizados.
- Corte de métricas del propio proyecto en la herramienta (bitácora #11): M-01 98.02 %, M-02 100 %, M-03 0, M-04 100 %, M-05 0 %, M-06 75 %; técnicas 81 %; semáforo **Amarillo**.


## Resumen del sprint 3

- Requisitos del check-in del 19 de noviembre: RF-16, RF-17 y RF-18, más el README (13.2), Docker (12.1) y las pruebas no funcionales (10.4).
- **Implementados (3):** RF-16 (#28, corregido en #30), RF-17 (#24, con la comparación desde #30) y RF-18 (#29).
- **Sigue en progreso (3):** RF-09 y RF-10 (D-01 y D-02) y RF-20 (D-03, D-04 y D-06), sin cambios desde el sprint 2.
- Pruebas en main al 19/11 (`5fecfb2`, CI #82): 349 aprobadas, ruff sin errores y cobertura 98.14 %.
- **Proceso (M-05):** de los PR #24 a #30, solo el #29 tiene el checklist completo (4 de 4): 1 / 7 = 14 %. Los PR #24, #26 y #30 tienen 3 de 4, y los #25, #27 y #28 no tienen checklist. Los 7 tienen aprobación. El PR #31 sigue abierto y necesita la aprobación de otro integrante y un `Closes #N` real.
- **Pruebas no funcionales (tarea 10.4):** RNF-01 y RNF-04 Passed; RNF-03 y RNF-05 Passed con observación; RNF-02, RNF-06 y RNF-07 pendientes. Informe: `Reporte_Pruebas_No_Funcionales_10.4.docx`.
