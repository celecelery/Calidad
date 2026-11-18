# Calidad

**Inicializar con Docker**

* Ve a la carpeta ArchivosPython
* Construye los contenedores con el siguiente comando:

```
	docker compose build
```

* Inicia la aplicación con el siguiente comando:
```
	docker compose up -d --build
```
 Y abre la aplicación en el 'localhost'

* Para realizar las migraciones, utiliza el siguiente comando:
```
	docker compose exec web python manage.py migrate
```

* Para apagar la aplicación, utiliza el siguiente comando:
```
	docker compose down
```