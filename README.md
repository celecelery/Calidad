# Calidad

**Deployment**
* Ve a la carpeta ArchivosPython
* En la terminal ejecuta los siguientes comando para crear y activar un entorno virtual:
```
	python -m venv venv
	.\venv\Scripts\Activate.ps1
```
* Instala los requerimientos de requirements.txt con el siguiente comando:
```
pip install -r requirements.txt
```
* Para iniciar el desarrollo del servidor, ejecuta el siguiente comando:
```
python manage.py runserver
```
   e ingresa a la dirección que aparece en la terminal

* Para realizar migraciones, utiliza el siguiente comando:
```
python manage.py migrate
```