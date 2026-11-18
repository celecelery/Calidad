# Dashboard de Monitoreo SQA

Aplicación web en Django para dar seguimiento a la calidad de los proyectos de software de un periodo: métricas por corte, técnicas SQA con su evidencia y un reporte de salud con semáforo (Rojo, Amarillo o Verde).

## Requisitos

Necesitas tener instalado Python 3.12 o una versión más nueva (con versiones anteriores Django no funciona) y Git. No hace falta instalar una base de datos porque el proyecto usa SQLite.

En Windows, al instalar Python marca la opción "Add python.exe to PATH". Si el comando `python` no funciona, usa `py` en su lugar.

## Instalación

Los comandos se escriben en la terminal (PowerShell en Windows).

### 1. Clonar el repositorio

```
git clone https://github.com/celecelery/Calidad.git
cd Calidad/archivosPython
```

Todos los pasos siguientes se hacen dentro de la carpeta `archivosPython`.

### 2. Crear y activar el entorno virtual

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En macOS o Linux se activa con `source venv/bin/activate`. El entorno virtual se crea una sola vez, pero hay que activarlo cada vez que abras una terminal nueva.

Si PowerShell no deja ejecutar `Activate.ps1`, corre `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a activarlo.

### 3. Instalar las dependencias

```
	docker compose up -d --build
```

La primera vez puede tardar unos 10 minutos.

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

El `.env` no se sube al repositorio.

### 5. Crear la base de datos

```
python manage.py migrate
```

Esto crea la base de datos y carga las métricas base (M-01 a M-06) y el catálogo de técnicas SQA.

### 6. Crear el primer Administrador

Primero crea la cuenta con la que vas a iniciar sesión:

```
python manage.py createsuperuser
```

Después hay que darle el perfil de Administrador. Abre la consola de Django con `python manage.py shell` y escribe lo siguiente, cambiando el usuario y el nombre por los tuyos:

```
from django.contrib.auth import get_user_model
from dashboard.models import Usuario
cuenta = get_user_model().objects.get(username="tu_usuario")
Usuario.objects.create(user=cuenta, nombre="Tu nombre", perfil="administrador")
exit()
```

Para los demás integrantes es lo mismo, pero con `perfil="miembro"`.

### 7. Iniciar el servidor

```
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en el navegador e inicia sesión con tu cuenta.

## Estructura del proyecto

- `archivosPython/`: el proyecto de Django; aquí se ejecutan todos los comandos.
  - `config/`: configuración del proyecto (settings y urls).
  - `cuentas/`: inicio y cierre de sesión.
  - `dashboard/`: la aplicación principal, con los modelos, vistas, plantillas y pruebas.
- `Bitacora SQA/`: bitácora, casos de prueba, matriz de trazabilidad y defectos.
- `.github/`: plantillas de issues y PR, y el CI.
