# Matriz de trazabilidad

Relaciona cada requisito de la Especificación de Requisitos v1.4 con su issue, el PR que lo implementa, sus casos de prueba (`casos_de_prueba.md`, tarea 10.2) y las pruebas automatizadas que lo verifican.
Se actualiza en cada PR que implementa o cambia un requisito.

**Estados:** Pendiente · En progreso · Implementado (fusionado en main con pruebas en verde) · Verificado (además pasó la revisión de QA)

**Última actualización:** 03/11/2026 — tarea 10.2: casos de prueba de RF-05 a RF-15 y RF-20; RF-08 (#14), RF-11 y RF-12 (#16), RF-05, RF-13, RF-14 y RF-15 (#17) fusionados

## Requisitos funcionales

| ID | Requisito | Check-in | Issue | PR | Casos (10.2) | Prueba | Estado |
|---|---|---|---|---|---|---|---|
| RF-01 | Registrar un periodo; no se guarda si la fecha de fin es anterior a la de inicio | 20 oct | Sin issue (por crear) | #9 | — | `dashboard/test_formularios.py`: `PeriodoFormTests`, `VistasFormulariosTests.test_post_periodo_*` | Verificado |
| RF-02 | Registrar un proyecto; nombre y periodo obligatorios, nombre único por periodo | 20 oct | Sin issue (por crear) | #9, #10 | — | `dashboard/test_formularios.py`: `ProyectoFormTests`, `VistasFormulariosTests.test_post_proyecto_*`; `dashboard/test_modelos.py` | Verificado |
| RF-03 | Editar los datos de un proyecto sin afectar a otros | 20 oct | Sin issue (por crear) | #11 | — | `dashboard/test_proyectos.py`: `EditarProyectoTests` | Verificado |
| RF-04 | Listar proyectos filtrando por periodo y estado | 20 oct | Sin issue (por crear) | #11 | — | `dashboard/test_proyectos.py`: `ListaProyectosTests` | Verificado |
| RF-05 | Archivar un proyecto sin borrarlo; se puede reactivar | 3 nov | Por crear | #17 | CP-05-01 a CP-05-04 | `dashboard/test_archivar.py`: `ModeloArchivarTests`, `VistaArchivarTests`, `VistaReactivarTests`, `PantallasArchivarTests` | Implementado |
| RF-06 | Administrar el catálogo de métricas | 3 nov | Por crear | #13 | CP-06-01 a CP-06-04 | `dashboard/test_metricas.py`: `MetricaFormTests`, `CatalogoVistasTests`, `MetaTextoTests`, `CumpleMetaTests` | Implementado |
| RF-07 | Asignar las 6 métricas base a un proyecto nuevo | 3 nov | Por crear | #13 | CP-07-01 a CP-07-03 | `dashboard/test_metricas.py`: `MetricasBaseTests`, `AsignacionMetricasTests` | Implementado |
| RF-08 | Capturar la medición de una métrica en un corte | 3 nov | Por crear | #14 | CP-08-01 a CP-08-07 | `dashboard/test_mediciones.py`: `MedicionFormTests`, `CorteFormTests`, `CapturarMedicionVistaTests`, `AgregarCorteVistaTests`, `TablaMedicionesTests` | Implementado |
| RF-09 | Graficar la evolución de cada métrica contra su meta | 3 nov | — | — | CP-09-01, CP-09-02 | Pendiente de implementar (tarea 7.3) | Pendiente |
| RF-10 | Resumen de proyectos activos con semáforo en el dashboard | 3 nov | — | — | CP-10-01 a CP-10-03 | Pendiente de implementar (tarea 7.3) | Pendiente |
| RF-11 | Catálogo de técnicas SQA (al menos 8 precargadas) | 3 nov | Por crear | #16 | CP-11-01 a CP-11-03 | `dashboard/test_tecnicas.py`: `CatalogoPrecargadoTests`, `TecnicaSQAFormTests`, `CatalogoVistasTests` | Implementado |
| RF-12 | Asignar técnicas a un proyecto con responsable y frecuencia | 3 nov | Por crear | #16 | CP-12-01 a CP-12-03 | `dashboard/test_tecnicas.py`: `AsignacionTecnicaFormTests`, `TecnicasProyectoVistaTests` | Implementado |
| RF-13 | Registrar la aplicación de una técnica con evidencia | 3 nov | Por crear | #17 | CP-13-01 a CP-13-04 | `dashboard/test_aplicaciones.py`: `AplicacionFormTests`, `RegistrarAplicacionVistaTests` | Implementado |
| RF-14 | Calcular el porcentaje de cumplimiento de técnicas | 3 nov | Por crear | #17 | CP-14-01 a CP-14-07 | `dashboard/test_aplicaciones.py`: `EsperadasTests`, `PorcentajeTests`, `PestanaTecnicasCumplimientoTests`, `PrsFusionadosTests` | Implementado |
| RF-15 | Generar el reporte de salud de un proyecto en un corte | 3 nov | Por crear | #17 | CP-15-01 a CP-15-13; flujo completo CP-INT-01 a CP-INT-06 | `dashboard/test_reporte_salud.py`: `CalcularSemaforoTests`, `ReporteDeSaludTests`, `ReporteVistaTests`. Flujo completo: por automatizar (10.3) | Implementado |
| RF-16 | Comparar el reporte con el corte anterior | 19 nov | — | — | — | — | Pendiente |
| RF-17 | Exportar el reporte a PDF | 19 nov | — | — | — | — | Pendiente |
| RF-18 | Historial de reportes de un proyecto | 19 nov | — | — | — | — | Pendiente |
| RF-19 | Iniciar y cerrar sesión; sin sesión se redirige al login | 20 oct | Sin issue (por crear) | #7 | — | `cuentas/tests.py`; `dashboard/tests.py`: `InicioTests` | Verificado |
| RF-20 | Perfiles Administrador y Miembro; un Miembro no puede editar catálogos | 3 nov | — | — | CP-20-01 a CP-20-05 | Pendiente de implementar (tarea 6.5) | Pendiente |

## Requisitos no funcionales

| ID | Requisito | Verificación | Issue | PR | Prueba / evidencia | Estado |
|---|---|---|---|---|---|---|
| RNF-01 | El dashboard carga en menos de 3 s con 20 proyectos | Prueba cronometrada en la beta | — | — | — | Pendiente |
| RNF-02 | Un usuario nuevo registra un proyecto en menos de 2 min | Prueba con un compañero ajeno al equipo | — | — | — | Pendiente |
| RNF-03 | Contraseñas con hash de Django; ninguna credencial en el repositorio | Revisión de código y uso de `.env` | Sin issue | #7 (hash); commit `e50b91f` (`.env` y `.env.example`, directo a main antes de proteger la rama) | `cuentas/tests.py::test_contrasena_guardada_con_hash`; revisión del historial (bitácora #6) | Implementado |
| RNF-04 | Los formularios validan en el servidor | Pruebas unitarias de formularios | Sin issue | #9, #11 | `dashboard/test_formularios.py`, `dashboard/test_proyectos.py` (envían datos inválidos por POST) | Verificado para RF-01 a RF-03; se repite en cada formulario nuevo |
| RNF-05 | Ruff sin errores y pruebas automatizadas en cada módulo | GitHub Actions en cada PR | Sin issue | #3, #4 (`ci.yml`) | Check "Ruff, pruebas y cobertura" requerido en main | En progreso (las apps `proyectos`, `metricas`, `tecnicas` y `reportes` todavía no tienen código ni pruebas) |
| RNF-06 | Funciona en Chrome, Firefox y Edge actuales | Prueba manual antes de la entrega final | — | — | — | Pendiente |
| RNF-07 | Se instala siguiendo solo el README | Un integrante instala desde cero | — | — | `README.md` existe; falta la prueba de instalación desde cero | En progreso |

## Resumen del sprint 1

- Requisitos del check-in del 20 de octubre: RF-01, RF-02, RF-03, RF-04 y RF-19. Los 5 están verificados.
- Ningún requisito tiene issue. Al crearlos, cambia "Sin issue (por crear)" por el número y edita el PR para agregar `Closes #número`.
- Pruebas en main al cierre: 51 aprobadas, ruff sin errores y cobertura del 98%.
