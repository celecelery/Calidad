# Defectos del proyecto (sprints 1, 2 y 3)

Todos los defectos que encontró QA durante el proyecto. Cada uno indica el sprint en que se encontró: **Sprint 1** (revisión del modelo de datos, bitácora #2, y la configuración inicial de CI), **Sprint 2** (revisión del 05/11/2026 y prueba interna, bitácora #7 a #11) y **Sprint 3** (revisión del 19/11/2026, bitácora #13 a #15). Los números no cambian aunque se hayan encontrado después; por eso D-11 a D-15 son del Sprint 1.

**Verificación del 19/11/2026 (tarea 11.6):** cada defecto se comprobó contra `main` (commit `5fecfb2`, fusión del PR #30) y las corridas de CI contra GitHub Actions. D-01, D-02, D-03, D-04, D-05 y D-06 **siguen presentes en main** (D-05 se reprodujo renderizando la plantilla con Django). Se corrigió el texto de D-02 (la plantilla sí cierra `</script>`; se quitó esa frase) y las líneas de código citadas. D-07, D-08 y D-09 existen en Actions, pero el registro del paso que falló solo se ve con sesión iniciada en GitHub: la causa queda **por confirmar** y no se inventó. Se agregó D-10 (Sprint 3: fallos de CI de los PR #25 y #28) D-11 a D-15 y D-16 a D-20 (Sprint 1, tomados de la bitácora #2 y de Actions) y D-21 a D-25 (hallazgos de las tareas 10.4 y 11.6 y de las bitácoras #6, #7 y #14). D-16 a D-25 se verificaron en `main` el 19/11/2026.
Cada uno se abre en GitHub con la plantilla **Defecto** (`.github/ISSUE_TEMPLATE/defecto.yml`), copiando los campos tal como están aquí.
Al abrirlo, se anota su número en la columna **Issue** y en la matriz de trazabilidad.

**Base de M-04 del corte del 04/11/2026:** los 9 defectos originales tienen criterios de aceptación → 9 / 9 = **100 %**. Con D-10 a D-25 serían 25 / 25 = 100 %.
Ese valor solo es válido si los defectos se abren en GitHub; si no se abren, M-04 vuelve a ser «no medible» (0 issues), como en el sprint 1.

**Severidad (de la plantilla):** Crítica = impide usar una función principal, pierde o corrompe datos, o es un problema de seguridad. Ninguno se clasificó como Crítico; el motivo está en D-03. Si el equipo decide etiquetar alguno como `crítico`, M-03 pasa a 1 y el semáforo del corte cambia a **Rojo**.

| ID | Sprint | Issue | Título | Módulo | Severidad | Requisito | Estado al abrir |
|---|---|---|---|---|---|---|---|
| D-01 | Sprint 2 | Por abrir | [Defecto] Inicio no muestra el semáforo de los proyectos | Módulo 4 | Mayor | RF-10 | Abierto |
| D-02 | Sprint 2 | Por abrir | [Defecto] La página de gráficas por métrica sale en blanco | Módulo 2 | Mayor | RF-09 | Abierto |
| D-03 | Sprint 2 | Por abrir | [Defecto] Un Miembro puede crear y editar métricas, técnicas y periodos | Transversal | Mayor | RF-20 | Abierto |
| D-04 | Sprint 2 | Por abrir | [Defecto] No hay forma de dar perfil a un usuario desde la aplicación | Transversal | Mayor | RF-20 | Abierto |
| D-05 | Sprint 2 | Por abrir | [Defecto] Mediciones da error 500 si una medición no tiene quién la capturó | Módulo 2 | Mayor | RF-08 | Abierto |
| D-06 | Sprint 2 | Por abrir | [Defecto] Las pruebas crean perfiles con valores fuera de las opciones | Transversal | Menor | RF-20 / RNF-05 | Abierto |
| D-07 | Sprint 2 | Por abrir | [Defecto] CI falló en el PR #15 (corrida #37) | Módulo 3 | Menor | RNF-05 | Cerrado (el PR se cerró y lo reemplazó el #16, con CI en verde) |
| D-08 | Sprint 2 | Por abrir | [Defecto] CI falló 3 veces en el PR #19 (corridas #45, #46 y #48) | Transversal | Menor | RNF-05 | Cerrado (corrida #50 en verde antes de fusionar) |
| D-09 | Sprint 2 | Por abrir | [Defecto] CI falló 3 veces en el PR #22 (corridas #57, #58 y #59) | Módulo 2 / 4 | Menor | RNF-05 | Cerrado (corrida #60 en verde antes de fusionar) |
| D-10 | Sprint 3 | Por abrir | [Defecto] CI falló en los PR #25 (corridas #66, #67 y #68) y #28 (corrida #76) | Transversal / Módulo 2 | Menor | RNF-05 | Cerrado (corridas #69 y #77 en verde antes de fusionar) |
| D-11 | Sprint 1 | Por abrir | [Defecto] El modelo de datos no migraba: llaves compuestas con campos inexistentes | Transversal | Mayor | RF-02 | Cerrado (corregido en el PR #11) |
| D-12 | Sprint 1 | Por abrir | [Defecto] La meta de una métrica y el valor de una medición eran texto | Módulo 2 | Mayor | RF-06 / RF-08 | Cerrado (corregido en el PR #11) |
| D-13 | Sprint 1 | Por abrir | [Defecto] La aplicación de una técnica no estaba ligada a su asignación | Módulo 3 | Mayor | RF-14 | Cerrado (corregido en el PR #11) |
| D-14 | Sprint 1 | Por abrir | [Defecto] La técnica SQA no tenía nombre | Módulo 3 | Menor | RF-11 | Cerrado (corregido en el PR #11) |
| D-15 | Sprint 1 | Por abrir | [Defecto] CI falló al configurarlo y en el PR #8 (corridas #1, #2, #7, #8, #18 y #19) | Transversal | Menor | RNF-05 | Cerrado (las corridas posteriores pasan) |
| D-16 | Sprint 1 | Por abrir | [Defecto] `corte` y `semaforo` de `ReporteSalud` son texto libre | Módulo 4 | Menor | RF-15 / RF-18 | Abierto |
| D-17 | Sprint 1 | Por abrir | [Defecto] `Proyecto.integrantes` es un número, no una lista de integrantes | Módulo 1 | Menor | RF-02 | Abierto |
| D-18 | Sprint 1 | Por abrir | [Defecto] Los modelos están en `dashboard` y las apps `proyectos`, `metricas`, `tecnicas` y `reportes` están vacías | Transversal | Menor | RNF-05 | Abierto |
| D-19 | Sprint 1 | Por abrir | [Defecto] `TIME_ZONE` está en UTC | Transversal | Menor | RF-08 | Abierto |
| D-20 | Sprint 1 | Por abrir | [Defecto] Existía un modelo `Usuario` propio sin ligar al usuario de Django | Transversal | Menor | RF-19 / RF-20 | Cerrado (ya se liga con `Usuario.user`; lo que falta es D-04) |
| D-21 | Sprint 3 | Por abrir | [Defecto] La contraseña `mypassword` está por omisión en archivos versionados | Transversal | Mayor | RNF-03 | Abierto |
| D-22 | Sprint 3 | Por abrir | [Defecto] La `SECRET_KEY` anterior sigue en el historial de git | Transversal | Menor | RNF-03 | Abierto |
| D-23 | Sprint 1 | Por abrir | [Defecto] El repositorio no tiene issues: ningún requisito ni defecto está registrado | Transversal | Mayor | M-04 / M-05 | Abierto |
| D-24 | Sprint 3 | Por abrir | [Defecto] Seis de los siete PR #24 a #30 no tienen el checklist completo | Transversal | Menor | M-05 | Abierto |
| D-25 | Sprint 2 | Por abrir | [Defecto] Los PR #17 y #18 usan `Closes #18` y `Closes #19`, que son PR y no issues | Transversal | Menor | M-05 | Cerrado (informativo; no se puede corregir en PR ya fusionados) |

---

## D-01 · [Defecto] Inicio no muestra el semáforo de los proyectos

- **Módulo:** Módulo 4 — Reportes de salud
- **Severidad:** Mayor (el semáforo sí se ve en el reporte de salud de cada proyecto)
- **Requisito afectado:** RF-10 (casos CP-10-01 y CP-10-02)

**Pasos para reproducir**
1. Registrar un proyecto, agregar un corte y capturar sus 6 métricas.
2. Abrir el reporte de salud del proyecto: muestra el semáforo (en la prueba interna, Amarillo).
3. Abrir Inicio.

**Resultado esperado**
Cada proyecto activo aparece en una fila con su semáforo actual, igual al de su reporte de salud. Los proyectos archivados no aparecen.

**Resultado actual**
- La columna Semáforo sale vacía: la vista `inicio` lee `ReporteSalud.objects`, pero ninguna parte del sistema guarda reportes (el reporte se calcula; el historial es RF-18). Ya existe `salud.semaforo_actual(proyecto)` para esto.
- El `{% for %}` de `inicio.html` no abre `<tr>`, así que las celdas se recorren una columna (el nombre queda bajo la columna del número de fila) y todos los proyectos quedan en el mismo renglón.
- Los proyectos archivados sí se listan (con estado «Archivado»).

**Criterios de aceptación**
- [ ] Inicio muestra una fila por proyecto activo con su semáforo, calculado con `semaforo_actual` (CP-10-01)
- [ ] Un proyecto archivado no aparece en Inicio (CP-10-02)
- [ ] Un proyecto sin cortes aparece con «Sin cortes» en lugar del semáforo
- [ ] Existen pruebas automatizadas de CP-10-01 y CP-10-02

---

## D-02 · [Defecto] La página de gráficas por métrica sale en blanco

- **Módulo:** Módulo 2 — Seguimiento de métricas
- **Severidad:** Mayor
- **Requisito afectado:** RF-09 (casos CP-09-01 y CP-09-02)

**Pasos para reproducir**
1. Proyecto con al menos un corte y mediciones capturadas.
2. Abrir `/proyectos/<id>/graficas/` (no hay enlace: la pestaña Evolución sigue deshabilitada con «Próximamente (RF-09)»).

**Resultado esperado**
Una gráfica por métrica con un punto por corte y la línea de meta, dentro del diseño de la aplicación y con la pestaña Evolución activa.

**Resultado actual**
Página sin contenido. `proyecto_grafica.html` solo contiene el `<script>` de Chart.js: no extiende `base.html`, no tiene los `<canvas id="grafica-N">`, no tiene el `json_script` con id `datos-graficas` que lee el script. La vista `grafica_metricas` (views.py, líneas 517–545) no tiene pruebas. Chart.js se carga desde un CDN, así que sin internet tampoco dibujaría.

**Criterios de aceptación**
- [ ] La plantilla extiende `base.html`, incluye las pestañas y dibuja una gráfica por métrica (CP-09-01)
- [ ] Un corte sin medición no dibuja punto (CP-09-02)
- [ ] La pestaña Evolución enlaza a la página
- [ ] Existen pruebas automatizadas de la vista y de los datos que manda a la plantilla

---

## D-03 · [Defecto] Un Miembro puede crear y editar métricas, técnicas y periodos

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Mayor. Por la definición de la plantilla podría ser Crítica (es un control de acceso), pero RF-20 todavía no está entregado (la tarea 6.5 está en progreso y el PR #19 lo implementó en parte). **Si se declara terminada la tarea 6.5 sin corregir esto, se reclasifica como Crítico.**
- **Requisito afectado:** RF-20 (casos CP-20-01 y CP-20-02)

**Pasos para reproducir**
1. Iniciar sesión con una cuenta cuyo `Usuario` tiene perfil `miembro`.
2. Catálogos › Métricas › editar M-01 y cambiar la meta de 70 a 10; guardar.
3. Catálogos › Técnicas SQA › Nueva técnica; guardar. Administración › Periodos › registrar un periodo; guardar.

**Resultado esperado**
Acceso denegado en los tres casos: un Miembro no puede editar catálogos (criterio de aceptación de RF-20).

**Resultado actual**
Los tres se guardan. La meta de M-01 quedó en 10 y cambia el semáforo de todos los proyectos. Solo `editar_proyecto`, `quitar_metrica` y `editar_tecnica` revisan el perfil; `metricas_view`, `tecnica_nueva` y `periodo_view` no.

**Criterios de aceptación**
- [ ] Un Miembro no puede crear ni editar métricas (CP-20-01)
- [ ] Un Miembro no puede crear ni editar técnicas ni periodos (CP-20-02)
- [ ] Un Miembro sí puede capturar mediciones y registrar aplicaciones (CP-20-03)
- [ ] Un Administrador sí puede editar catálogos y periodos (CP-20-04)
- [ ] Existen pruebas automatizadas de los cuatro casos

---

## D-04 · [Defecto] No hay forma de dar perfil a un usuario desde la aplicación

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Mayor
- **Requisito afectado:** RF-20 (caso CP-20-05). Es el defecto que el PR #14 reportó sin número.

**Pasos para reproducir**
1. Base nueva: `python manage.py migrate` y `python manage.py createsuperuser`.
2. Iniciar sesión e ir a Registrar proyecto.
3. Intentar editar un proyecto.

**Resultado esperado**
La lista «Líder» ofrece a los usuarios registrados y hay una forma desde la aplicación (o desde `/admin/`) de darle a una cuenta el perfil Administrador o Miembro.

**Resultado actual**
La lista «Líder» está vacía, así que no se puede registrar ningún proyecto, y el superusuario no puede editar proyectos porque no tiene `Usuario` ligado. `dashboard/admin.py` está vacío y no hay pantalla de usuarios: en la prueba interna hubo que crear los `Usuario` y el perfil desde `manage.py shell`.

**Criterios de aceptación**
- [ ] Un Administrador puede crear un `Usuario`, ligarlo a una cuenta y elegir su perfil sin usar el shell
- [ ] La lista «Líder» ofrece a los usuarios registrados en una base nueva (CP-20-05)
- [x] El README explica cómo crear el primer Administrador (tarea 13.2, con `manage.py shell` mientras no exista la pantalla)
- [ ] Existe una prueba automatizada que cubre el caso

---

## D-05 · [Defecto] Mediciones da error 500 si una medición no tiene quién la capturó

- **Módulo:** Módulo 2 — Seguimiento de métricas
- **Severidad:** Mayor (la pestaña Mediciones del proyecto deja de abrir)
- **Requisito afectado:** RF-08

**Pasos para reproducir**
1. Capturar una medición con una cuenta y luego borrar esa cuenta (`capturado_por` usa `on_delete=SET_NULL`), o cargar una medición sin `capturado_por` desde el shell o un script.
2. Abrir Proyecto › Mediciones.

**Resultado esperado**
La página abre y la columna «Capturó» muestra «—».

**Resultado actual**
Error 500 (`VariableDoesNotExist: Failed lookup for key [get_username] in None`) en `metricas_proyecto.html`, línea 92: `fila.ultima.capturado_por.get_username` se usa como argumento de `default` y falla cuando `capturado_por` es `None`.

**Criterios de aceptación**
- [ ] Mediciones abre con una medición sin `capturado_por` y muestra «—»
- [ ] Existe una prueba automatizada que cubre el caso

---

## D-06 · [Defecto] Las pruebas crean perfiles con valores fuera de las opciones

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** RF-20 / RNF-05

**Pasos para reproducir**
1. Buscar `perfil="Administrador"` y `perfil="Miembro"` en `dashboard/test_*.py` (`test_integracion.py:37`, `test_aplicaciones.py:34-35`, `test_proyectos.py:22-23`, `test_tecnicas.py:116-117`, `test_formularios.py`, `test_mediciones.py`).

**Resultado esperado**
Las pruebas usan los valores de `Usuario.PERFIL_CHOICES` (`administrador` y `miembro`).

**Resultado actual**
Usan mayúscula inicial. Hoy no falla nada porque solo se compara con `"administrador"`, pero un usuario de prueba con `"Administrador"` se trata como si no tuviera perfil, y una prueba de permisos puede pasar por el motivo equivocado.

**Criterios de aceptación**
- [ ] Ninguna prueba crea un `Usuario` con un perfil fuera de `PERFIL_CHOICES`
- [ ] `Usuario.full_clean()` rechaza un perfil fuera de las opciones (prueba automatizada)

---

## D-07 · [Defecto] CI falló en el PR #15 (corrida #37)

- **Módulo:** Módulo 3 — Gestión de técnicas SQA
- **Severidad:** Menor (no llegó a main)
- **Requisito afectado:** RNF-05
- **Estado:** se abre y se cierra: el PR #15 se cerró sin fusionar y lo reemplazó el PR #16, que pasó CI.

**Pasos para reproducir**
1. GitHub › Actions › corrida #37 («Rf 11 y rf 12», rama `RF-11-y-RF-12`).

**Resultado esperado**
El check «Ruff, pruebas y cobertura» en verde.

**Resultado actual**
El check «Ruff, pruebas y cobertura» falló en 34 s con la anotación «Process completed with exit code 1». El paso exacto (ruff, pruebas o cobertura) **está por confirmar**: el registro del paso solo se abre con sesión iniciada en GitHub.

**Criterios de aceptación**
- [ ] La causa está anotada en el issue con el paso que falló (ruff, pruebas o cobertura)
- [ ] El PR que reemplaza al #15 (#16) tiene CI en verde

---

## D-08 · [Defecto] CI falló 3 veces en el PR #19 (corridas #45, #46 y #48)

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor (se corrigió antes de fusionar)
- **Requisito afectado:** RNF-05
- **Estado:** se abre y se cierra: la corrida #50 pasó y el PR se fusionó en verde.

**Pasos para reproducir**
1. GitHub › Actions › corridas #45, #46 y #48 («Opciones de Administrador y Miembro agregados al modelo Usuario», rama `admin_y_miembro`).

**Resultado esperado**
El check en verde desde que se abre el PR (correr `ruff check .` y `pytest` antes de subir).

**Resultado actual**
Tres corridas seguidas fallaron (#45, #46 y #48; 27 s, 27 s y 48 s). La causa de cada una **está por confirmar** (el registro solo se abre con sesión iniciada en GitHub).

**Criterios de aceptación**
- [ ] La causa de cada falla está anotada en el issue
- [ ] La corrida final del PR (#50) está en verde

---

## D-09 · [Defecto] CI falló 3 veces en el PR #22 (corridas #57, #58 y #59)

- **Módulo:** Módulo 2 — Seguimiento de métricas / Módulo 4 — Reportes de salud
- **Severidad:** Menor (se corrigió antes de fusionar)
- **Requisito afectado:** RNF-05
- **Estado:** se abre y se cierra: la corrida #60 pasó y el PR se fusionó en verde.

**Pasos para reproducir**
1. GitHub › Actions › corridas #57, #58 y #59 («pestaña de grafica y menu de semaforo», rama `grafica_semaforo_inicio`).

**Resultado esperado**
El check en verde desde que se abre el PR.

**Resultado actual**
Tres corridas seguidas fallaron (#57, #58 y #59; 32 s, 50 s y 1 min 30 s). La causa de cada una **está por confirmar** (el registro solo se abre con sesión iniciada en GitHub). La corrida #60 del mismo PR pasó.

**Criterios de aceptación**
- [ ] La causa de cada falla está anotada en el issue
- [ ] La corrida final del PR (#60) está en verde

---

## D-10 · [Defecto] CI falló en los PR #25 (corridas #66, #67 y #68) y #28 (corrida #76)

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor (se corrigió antes de fusionar)
- **Requisito afectado:** RNF-05
- **Estado:** se abre y se cierra: la corrida #69 (PR #25) y la #77 (PR #28) pasaron y los PR se fusionaron en verde.

**Pasos para reproducir**
1. GitHub › Actions › corridas #66, #67 y #68 («Archivos de Docker agregados», rama `docker_implementado`, PR #25) y corrida #76 («RF-16. Comparación de métrica por corte», rama `comparacion_cortes`, PR #28).

**Resultado esperado**
El check en verde desde que se abre el PR (correr `ruff check .` y `pytest` antes de subir).

**Resultado actual**
Cuatro corridas fallaron (#66 en 18 s, #67 en 14 s, #68 en 1 min 6 s y #76 en 44 s). La causa de cada una **está por confirmar** (el registro solo se abre con sesión iniciada en GitHub).

**Criterios de aceptación**
- [ ] La causa de cada falla está anotada en el issue
- [ ] La corrida final de cada PR (#69 y #77) está en verde

---

## D-11 · [Defecto] El modelo de datos no migraba: llaves compuestas con campos inexistentes

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Mayor (bloqueaba las migraciones; no llegó a producción)
- **Requisito afectado:** RF-02 (nombre único por periodo)
- **Encontrado en:** Sprint 1, revisión del modelo de datos (bitácora #2, 20/10/2026)

**Pasos para reproducir**
1. Con el modelo de datos de la tarea 4.3, ejecutar `python manage.py makemigrations`.

**Resultado esperado**
Se generan las migraciones.

**Resultado actual**
Errores E042 (`CompositePrimaryKey` con campos inexistentes en `Proyecto`, `AsignacionTecnica` y `MetricaProyecto`) y E347 (relaciones hacia un modelo con llave compuesta): `makemigrations` no corría.

**Criterios de aceptación**
- [x] `makemigrations` y `migrate` corren sin errores
- [x] Las llaves son `id` automáticas con `UniqueConstraint` (nombre único por periodo y una medición por métrica y corte)
- [x] Corregido con la migración `0002_correcciones_modelo` (PR #11)

---

## D-12 · [Defecto] La meta de una métrica y el valor de una medición eran texto

- **Módulo:** Módulo 2 — Seguimiento de métricas
- **Severidad:** Mayor
- **Requisito afectado:** RF-06 / RF-08
- **Encontrado en:** Sprint 1, revisión del modelo de datos (bitácora #2)

**Resultado esperado**
`Metrica.meta` y `MetricaProyecto.valor` son numéricos, para validar rangos (RF-08) y graficar.

**Resultado actual**
Eran campos de texto, lo que impedía validar rangos y graficar.

**Criterios de aceptación**
- [x] Ambos campos son decimales (migración `0002_correcciones_modelo`, PR #11)

---

## D-13 · [Defecto] La aplicación de una técnica no estaba ligada a su asignación

- **Módulo:** Módulo 3 — Gestión de técnicas SQA
- **Severidad:** Mayor
- **Requisito afectado:** RF-14
- **Encontrado en:** Sprint 1, revisión del modelo de datos (bitácora #2)

**Resultado esperado**
Cada `AplicacionTecnica` pertenece a la asignación de una técnica a un proyecto, para calcular el cumplimiento.

**Resultado actual**
`AplicacionTecnica` no tenía relación con la asignación, así que no se podía calcular el cumplimiento.

**Criterios de aceptación**
- [x] `AplicacionTecnica` tiene una llave foránea obligatoria a la asignación (migración `0002`, PR #11)

---

## D-14 · [Defecto] La técnica SQA no tenía nombre

- **Módulo:** Módulo 3 — Gestión de técnicas SQA
- **Severidad:** Menor
- **Requisito afectado:** RF-11
- **Encontrado en:** Sprint 1, revisión del modelo de datos (bitácora #2)

**Resultado esperado**
Cada técnica del catálogo tiene un nombre.

**Resultado actual**
`TecnicaSQA` no tenía el campo nombre.

**Criterios de aceptación**
- [x] `TecnicaSQA` tiene nombre (migración `0002`, PR #11)

---

## D-15 · [Defecto] CI falló al configurarlo y en el PR #8 (corridas #1, #2, #7, #8, #18 y #19)

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** RNF-05
- **Encontrado en:** Sprint 1, configuración de CI (tarea 5.3)

**Pasos para reproducir**
1. GitHub › Actions › corridas #1 («Create ci.yml»), #2 («Set working directory for CI job»), #7 («5.3: correr CI en cada push y pull request»), #8 («Merge branch 'main' into configuraciones_pytest») y #18 y #19 (PR #8, «Feature/dashboard»).

**Resultado esperado**
El check «Ruff, pruebas y cobertura» en verde.

**Resultado actual**
Las seis corridas fallaron. La causa de cada una **está por confirmar** (el registro solo se abre con sesión iniciada en GitHub). Las corridas posteriores de `main` y de los PR siguientes pasan.

**Criterios de aceptación**
- [ ] La causa de cada falla está anotada en el issue

---

## D-16 · [Defecto] `corte` y `semaforo` de `ReporteSalud` son texto libre

- **Módulo:** Módulo 4 — Reportes de salud
- **Severidad:** Menor
- **Requisito afectado:** RF-15 / RF-18
- **Encontrado en:** Sprint 1, revisión del modelo de datos (bitácora #2, observaciones a y b); verificado en `main` el 19/11/2026

**Pasos para reproducir**
1. Abrir `archivosPython/dashboard/models.py`, clase `ReporteSalud` (líneas 126 y 127).

**Resultado esperado**
`semaforo` solo admite Verde, Amarillo o Rojo (con `choices`) y `corte` apunta al modelo `Corte` (que tiene fecha), como dice el glosario.

**Resultado actual**
Los dos son `CharField(max_length=50)` y admiten cualquier texto. Además, el sistema no guarda ningún `ReporteSalud` (el reporte se calcula en `salud.py`), de modo que el modelo solo lo lee la vista `inicio` (ver D-01). `tipo` y `sentido` de `Metrica` ya usan `choices`.

**Criterios de aceptación**
- [ ] `semaforo` tiene opciones fijas, o el modelo `ReporteSalud` se elimina si el reporte se sigue calculando
- [ ] `corte` es una llave foránea a `Corte`, o se elimina junto con el modelo
- [ ] Existe una prueba automatizada del cambio

---

## D-17 · [Defecto] `Proyecto.integrantes` es un número, no una lista de integrantes

- **Módulo:** Módulo 1 — Registro de proyectos
- **Severidad:** Menor
- **Requisito afectado:** RF-02
- **Encontrado en:** Sprint 1, revisión del modelo de datos (bitácora #2, observación d); verificado en `main` el 19/11/2026

**Pasos para reproducir**
1. Abrir `models.py`, clase `Proyecto` (línea 57): `integrantes = models.IntegerField(...)`.
2. Registrar un proyecto: el formulario pide un número.

**Resultado esperado**
Se sabe quiénes son los integrantes del proyecto, o la especificación acepta solo la cantidad.

**Resultado actual**
Solo se guarda la cantidad. La Especificación de Requisitos habla de integrantes, pero el sistema no puede decir quiénes son.

**Criterios de aceptación**
- [ ] El equipo decide (y deja anotado) si basta con la cantidad o se necesita la lista
- [ ] La especificación y el modelo dicen lo mismo

---

## D-18 · [Defecto] Los modelos están en `dashboard` y las apps `proyectos`, `metricas`, `tecnicas` y `reportes` están vacías

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** RNF-05
- **Encontrado en:** Sprint 1 (bitácora #2, observación e); confirmado en la tarea 10.4 el 19/11/2026

**Pasos para reproducir**
1. Abrir las carpetas `proyectos`, `metricas`, `tecnicas` y `reportes`: solo contienen los archivos que genera `startapp`.
2. Abrir `dashboard/models.py`, `views.py` y `urls.py`: todo el código está ahí.

**Resultado esperado**
Cada módulo del producto tiene su propia app con su código y sus pruebas, o las apps que no se usan se eliminan.

**Resultado actual**
Las cuatro apps suman 814 bytes de código en total y no tienen pruebas propias. Toda la lógica y las pruebas están en `dashboard`.

**Criterios de aceptación**
- [ ] El equipo decide mover el código a las apps o eliminar las vacías
- [ ] `INSTALLED_APPS` solo lista apps que tienen código

---

## D-19 · [Defecto] `TIME_ZONE` está en UTC

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** RF-08
- **Encontrado en:** Sprint 1 (bitácora #2, observación f); verificado en `main` el 19/11/2026

**Pasos para reproducir**
1. Abrir `config/settings.py`, línea 119: `TIME_ZONE = 'UTC'`.
2. Capturar una medición y ver la columna «Fecha de captura» (`capturado_en`).

**Resultado esperado**
Las fechas y horas se muestran en la zona del equipo (por ejemplo `America/Mexico_City`).

**Resultado actual**
Se muestran en UTC, seis horas adelante de México.

**Criterios de aceptación**
- [ ] `TIME_ZONE` tiene la zona del equipo
- [ ] Una prueba confirma la hora mostrada

---

## D-20 · [Defecto] Existía un modelo `Usuario` propio sin ligar al usuario de Django

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** RF-19 / RF-20
- **Encontrado en:** Sprint 1 (bitácora #2, observación c)

**Resultado esperado**
El perfil (Administrador o Miembro) pertenece a la cuenta con la que se inicia sesión.

**Resultado actual**
En el Sprint 1 había dos usuarios separados. Hoy `Usuario.user` es una `OneToOneField` al usuario de Django, así que la observación quedó resuelta. Lo que sigue pendiente es dar el perfil desde la aplicación (D-04).

**Criterios de aceptación**
- [x] `Usuario` está ligado al usuario de Django (`models.py`, línea 13)

---

## D-21 · [Defecto] La contraseña `mypassword` está por omisión en archivos versionados

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Mayor. La plantilla pone los problemas de seguridad como Críticos; se deja Mayor porque es una contraseña de desarrollo y `settings.py` ya exige `SECRET_KEY` desde el entorno. **Si se despliega con estos valores, se reclasifica como Crítico.**
- **Requisito afectado:** RNF-03
- **Encontrado en:** Sprint 3, tarea 10.4 (19/11/2026)

**Pasos para reproducir**
1. Buscar `mypassword` en el repositorio: aparece en `archivosPython/config/settings.py` (línea 88, como valor por omisión de `DB_PASSWORD`), en `archivosPython/docker-compose.yml` (líneas 18 y 49) y en `.github/workflows/ci.yml` (líneas 18 y 25).

**Resultado esperado**
Ninguna contraseña real ni por omisión en el repositorio; el valor sale de `.env`.

**Resultado actual**
Quien levante la base sin definir `DB_PASSWORD` usa `mypassword`, y el servidor de la demo con Docker quedaría con esa contraseña.

**Criterios de aceptación**
- [ ] `settings.py` no trae contraseña por omisión
- [ ] `docker-compose.yml` lee la contraseña desde `.env`
- [ ] El README indica definirla en `.env`

---

## D-22 · [Defecto] La `SECRET_KEY` anterior sigue en el historial de git

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor (la llave ya no se usa)
- **Requisito afectado:** RNF-03
- **Encontrado en:** Sprint 1 (bitácora #6), confirmado en la tarea 10.4 (19/11/2026)

**Pasos para reproducir**
1. `git show 670a646 -- archivosPython/config/settings.py` muestra la línea `SECRET_KEY = 'django-insecure-...'`.

**Resultado esperado**
Ninguna llave real en el historial.

**Resultado actual**
La llave original sigue en el commit `670a646`. El código actual la lee de `.env` (`config("SECRET_KEY")`) y `.env` nunca se subió.

**Criterios de aceptación**
- [ ] El equipo confirma que la llave anterior no se usa en ningún entorno (la demo incluida)
- [ ] La demo usa una llave nueva generada en su servidor

---

## D-23 · [Defecto] El repositorio no tiene issues: ningún requisito ni defecto está registrado

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Mayor (hace imposible medir M-04 y deja sin trazabilidad a los requisitos)
- **Requisito afectado:** M-04 / M-05
- **Encontrado en:** Sprint 1 (bitácora #6); sigue igual el 19/11/2026

**Pasos para reproducir**
1. Abrir GitHub › Issues: 0 abiertos y 0 cerrados.

**Resultado esperado**
Cada requisito y cada defecto tiene su issue con criterios de aceptación, y cada PR lo referencia con `Closes #N`.

**Resultado actual**
No existe ningún issue. Los números `#1` a `#31` del repositorio son todos PR.

**Criterios de aceptación**
- [ ] Se abren los issues de `issues_para_github.md`
- [ ] La matriz de trazabilidad tiene el número de cada uno
- [ ] M-04 se mide con los issues abiertos

---

## D-24 · [Defecto] Seis de los siete PR #24 a #30 no tienen el checklist completo

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** M-05
- **Encontrado en:** Sprint 3, revisión de PR (bitácora #14, 19/11/2026)

**Pasos para reproducir**
1. Abrir en GitHub los PR #24 a #30 y revisar la sección Checklist.

**Resultado esperado**
Los siete PR fusionados con las cuatro casillas marcadas (M-05 = 100 %).

**Resultado actual**
Solo el #29 tiene 4 de 4. Los #24, #26 y #30 tienen 3 de 4, y los #25, #27 y #28 no tienen checklist. M-05 del sprint = 1 / 7 = 14 %.

**Criterios de aceptación**
- [ ] Los PR nuevos (empezando por el #31) llevan el checklist completo antes de fusionarse
- [ ] Ninguna casilla de los PR ya fusionados se marca de forma retroactiva

---

## D-25 · [Defecto] Los PR #17 y #18 usan `Closes #18` y `Closes #19`, que son PR y no issues

- **Módulo:** Transversal (sesión, perfiles, despliegue, documentación)
- **Severidad:** Menor
- **Requisito afectado:** M-05
- **Encontrado en:** Sprint 2, revisión de PR (bitácora #7, 05/11/2026)

**Resultado esperado**
`Closes #N` apunta a un issue real.

**Resultado actual**
Como el repositorio no tenía issues, los números apuntan a PR; GitHub no cierra nada. Los PR ya están fusionados y no se corrigen; el defecto queda como registro y se evita en los PR nuevos (D-23).

**Criterios de aceptación**
- [x] Registrado; se evita en los PR del Sprint 3 en adelante
