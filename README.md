# Dashboard de Monitoreo SQA

Aplicación web en Django para dar seguimiento a la calidad de los proyectos de software de un periodo: métricas por corte, técnicas SQA con su evidencia y un reporte de salud con semáforo (Rojo, Amarillo o Verde).

## Requisitos

Necesitas tener instalado:

- Python 3.12 o una versión más nueva (con versiones anteriores Django no funciona).
- Git.
- Docker Desktop, para levantar la base de datos PostgreSQL 16 que usa el proyecto. Si prefieres instalar PostgreSQL directamente, crea la base `mydatabase` con el usuario `myuser` y la contraseña `mypassword` en el puerto 5432.

En Windows, al instalar Python marca la opción "Add python.exe to PATH". Si el comando `python` no funciona, usa `py` en su lugar.

## Instalación

Los comandos se escriben en la terminal (PowerShell en Windows, o la terminal en Linux).

### 1. Clonar el repositorio

```
git clone https://github.com/celecelery/Calidad.git
cd Calidad/archivosPython
```

Todos los pasos siguientes se hacen dentro de la carpeta `archivosPython`.

### 2. Crear y activar el entorno virtual

En Windows:

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En Linux:

```
python3 -m venv venv
source venv/bin/activate
```

El entorno virtual se crea una sola vez, pero hay que activarlo cada vez que abras una terminal nueva. Si PowerShell no deja ejecutar `Activate.ps1`, corre `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a activarlo.

### 3. Instalar las dependencias

```
pip install -r requirements.txt
```

La primera vez puede tardar unos 10 minutos. Esto también instala `ruff` y `pytest`, que se usan en la sección Pruebas y calidad.

### 4. Crear el archivo .env

Copia el archivo `.env.example` y renómbralo a `.env`. Después genera una clave secreta con este comando:

```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Pega la clave en `SECRET_KEY` dentro del `.env`. El archivo debe quedar así:

```
SECRET_KEY=la-clave-que-generaste
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

`SECRET_KEY` es obligatoria: sin ella el sistema no arranca. `DEBUG=True` es para trabajar en tu computadora y `ALLOWED_HOSTS` son las direcciones desde las que se puede abrir la aplicación. El `.env` no se sube al repositorio.

### 5. Levantar la base de datos

Con Docker Desktop abierto, levanta solo el servicio de PostgreSQL del `docker-compose.yml`:

```
docker compose up -d db
```

La aplicación se conecta a la base en `localhost:5432`, así que ese puerto debe estar publicado en el servicio `db` del `docker-compose.yml` (`ports: - "5432:5432"`). Para comprobar que la base está lista, corre `docker compose ps`: el servicio `db` debe aparecer como `running`.

### 6. Crear las tablas

```
python manage.py migrate
```

Esto crea las tablas y carga las métricas base (M-01 a M-06) y el catálogo de técnicas SQA. Si el comando dice que no puede conectarse a la base, revisa que `docker compose ps` muestre `db` en ejecución y que el puerto 5432 esté publicado (paso 5). Las migraciones ya vienen en el repositorio: no hace falta correr `makemigrations`.

### 7. Crear el superusuario y darle perfil

Primero crea la cuenta con la que vas a iniciar sesión:

```
python manage.py createsuperuser
```

Después dale perfil de Administrador. Sin perfil, el sistema no te deja editar proyectos ni administrar catálogos, y no apareces en la lista de líderes al registrar un proyecto. Abre la consola de Django:

```
python manage.py shell
```

Y escribe estas líneas, cambiando `tu_usuario` por el usuario que acabas de crear y `Nombre Apellido` por tu nombre:

```
from django.contrib.auth import get_user_model
from dashboard.models import Usuario
u = get_user_model().objects.get(username="tu_usuario")
Usuario.objects.update_or_create(user=u, defaults={"nombre": "Nombre Apellido", "perfil": "administrador"})
exit()
```

Para un Miembro usa `"perfil": "miembro"`.

### 8. Iniciar la aplicación

```
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador e inicia sesión con tu cuenta. Para apagar la aplicación, presiona `Ctrl+C` en la terminal donde corre.

## Pruebas y calidad

Son las mismas revisiones que hace el CI de GitHub en cada PR. Con el entorno virtual activo y la base de datos levantada:

```
ruff check .
pytest --cov=. --cov-report=term-missing --cov-fail-under=70
```

Ruff tiene que decir `All checks passed!`, todas las pruebas tienen que pasar y la cobertura tiene que ser de 70 % o más. Las pruebas crean su propia base temporal, así que no tocan tus datos.

## Despliegue

El proyecto corre completo en Docker. El `Dockerfile` arma la imagen de la aplicación con Python 3.12 y el `docker-compose.yml` levanta tres servicios: `web` (Django con Gunicorn, interno en el puerto 8000), `nginx` (publica la aplicación en el puerto 80 y sirve los archivos estáticos) y `db` (PostgreSQL 16, con sus datos en el volumen `postgres_data`).

Para desplegar en un servidor (o probarlo todo en Docker), clona el repositorio, entra a `archivosPython` y crea el `.env` como en el paso 4. En `ALLOWED_HOSTS` agrega la IP o el dominio del servidor, y pon `DEBUG=False`. El contenedor `web` lee el `.env` desde la carpeta del proyecto, que `docker-compose.yml` monta en `/app`. Después:

```
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
```

`collectstatic` copia los archivos estáticos (estilos y gráficas) al volumen que usa NGINX; sin ese paso la aplicación se ve sin estilos. El perfil del primer Administrador se da igual que en el paso 7, pero abriendo la consola con `docker compose exec web python manage.py shell`.

La aplicación queda en el puerto 80 del servidor: abre `http://IP-DEL-SERVIDOR/` (o `http://localhost/` si la probaste en tu computadora).

Para ver los mensajes de la aplicación usa `docker compose logs -f web`, y para detenerla `docker compose down`. Los datos se conservan en el volumen; `docker compose down -v` los borra.

## Estructura del proyecto

- `archivosPython/`: el proyecto de Django; aquí se ejecutan todos los comandos.
  - `config/`: configuración del proyecto (settings y urls).
  - `cuentas/`: inicio y cierre de sesión.
  - `dashboard/`: la aplicación principal, con los modelos, vistas, plantillas y pruebas. Las carpetas `proyectos/`, `metricas/`, `tecnicas/` y `reportes/` están vacías: toda la lógica vive en `dashboard/`.
  - `Dockerfile`, `docker-compose.yml` y `nginx/`: el despliegue con Docker.
- `Bitacora SQA/`: bitácora, casos de prueba, matriz de trazabilidad y defectos.
- `.github/`: plantillas de issues y PR, y el CI.
