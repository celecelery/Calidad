# Issues de la revisión del sprint 2 (tarea 11.4)

Defectos que encontró QA en la revisión del sprint 2 y en la prueba interna del corte del 04/11/2026 (bitácora #9 a #11).
Cada uno se abre en GitHub con la plantilla **Defecto** (`.github/ISSUE_TEMPLATE/defecto.yml`), copiando los campos tal como están aquí.
Al abrirlo, se anota su número en la columna **Issue** y en la matriz de trazabilidad.

**Base de M-04 del corte del 04/11/2026:** los 9 issues tienen criterios de aceptación → 9 / 9 = **100 %**.
Ese valor solo es válido si los 9 se abren en GitHub; si no se abren, M-04 vuelve a ser «no medible» (0 issues), como en el sprint 1.

**Severidad (de la plantilla):** Crítica = impide usar una función principal, pierde o corrompe datos, o es un problema de seguridad. Ninguno se clasificó como Crítico; el motivo está en D-03. Si el equipo decide etiquetar alguno como `crítico`, M-03 pasa a 1 y el semáforo del corte cambia a **Rojo**.

| ID | Issue | Título | Módulo | Severidad | Requisito | Estado al abrir |
|---|---|---|---|---|---|---|
| D-01 | Por abrir | [Defecto] Inicio no muestra el semáforo de los proyectos | Módulo 4 | Mayor | RF-10 | Abierto |
| D-02 | Por abrir | [Defecto] La página de gráficas por métrica sale en blanco | Módulo 2 | Mayor | RF-09 | Abierto |
| D-03 | Por abrir | [Defecto] Un Miembro puede crear y editar métricas, técnicas y periodos | Transversal | Mayor | RF-20 | Abierto |
| D-04 | Por abrir | [Defecto] No hay forma de dar perfil a un usuario desde la aplicación | Transversal | Mayor | RF-20 | Abierto |
| D-05 | Por abrir | [Defecto] Mediciones da error 500 si una medición no tiene quién la capturó | Módulo 2 | Mayor | RF-08 | Abierto |
| D-06 | Por abrir | [Defecto] Las pruebas crean perfiles con valores fuera de las opciones | Transversal | Menor | RF-20 / RNF-05 | Abierto |
| D-07 | Por abrir | [Defecto] CI falló en el PR #15 (corrida #37) | Módulo 3 | Menor | RNF-05 | Cerrado (el PR se cerró y lo reemplazó el #16, con CI en verde) |
| D-08 | Por abrir | [Defecto] CI falló 3 veces en el PR #19 (corridas #45, #46 y #48) | Transversal | Menor | RNF-05 | Cerrado (corrida #50 en verde antes de fusionar) |
| D-09 | Por abrir | [Defecto] CI falló 3 veces en el PR #22 (corridas #57, #58 y #59) | Módulo 2 / 4 | Menor | RNF-05 | Cerrado (corrida #60 en verde antes de fusionar) |

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
Página en blanco. `proyecto_grafica.html` solo contiene el `<script>` de Chart.js: no extiende `base.html`, no tiene los `<canvas id="grafica-N">`, no tiene el `json_script` con id `datos-graficas` que lee el script y no cierra `</script>`. La vista `grafica_metricas` (views.py, líneas 514–538) no tiene pruebas. Chart.js se carga desde un CDN, lo que falla sin internet en el servidor propio.

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
- [ ] El README explica cómo crear el primer Administrador
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
El check falló. *(Copiar aquí el paso que falló y el mensaje del log de la corrida #37.)*

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
Tres corridas seguidas fallaron. *(Copiar aquí el paso que falló y el mensaje del log de cada corrida.)*

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
Tres corridas seguidas fallaron. *(Copiar aquí el paso que falló y el mensaje del log de cada corrida.)*

**Criterios de aceptación**
- [ ] La causa de cada falla está anotada en el issue
- [ ] La corrida final del PR (#60) está en verde
