# Calidad

**Inicializar con Docker**

* Ve a la carpeta ArchivosPython
* Construye los contenedores con el siguiente comando:

```
	docker compose build
```

* Para coleccionar los archivos estaticos para el uso de NGINX, usa el siguiente comando:
```
	docker compose run --rm web python manage.py collectstatic --noinput
```

* Inicia la aplicación con el siguiente comando:
```
	docker compose up -d --build
```
 Y abre la aplicación en 'localhost'

* Para realizar las migraciones, utiliza el siguiente comando:
```
	docker compose exec web python manage.py migrate
```

* En caso de que haya problemas con las migraciones, utiliza el siguiente comando:
```
	docker compose exec web python manage.py makemigrations
```
 y vuelve a ejecutar el comando de migraciones.

* Para apagar la aplicación, utiliza el siguiente comando:
```
	docker compose down
```