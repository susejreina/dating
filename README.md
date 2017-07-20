## DateSite

**Antes de clonar el proyecto, _crear un entorno virtual._**

- Instalar Python 3
- Instalar PostgreSQL
	* user: postgres
	* password: superuser
	* port: 5432
- Instalar psycopg2 package (descargar)
	* `$ pip install psycopg2`
- Instalar Django
	* `$ pip install Django==1.10`


######  Crear y configurar la base de datos

- Abrir la consola y ejecutar
	* `$ setx PATH "%PATH%;C:\Program Files\PostgreSQL\9.3\bin" `
- Reiniciar la consola y ejecutar
	* ` psql -U postgres -W `
 	* ` pass: superuser `
- Una vez en la consola creamos el usuario para el administrador
	* `CREATE USER siteadmin;`
	* `ALTER ROLE siteadmin WITH PASSWORD '@dm!n';`
- Crear la base de datos:
	* ` CREATE DATABASE dating; `
	* con  `siteadmin` como owner
- Eliminar el esquema  `public`
- Crear el esquema  `dating`
- Configurar la base de datos en el proyecto:
- En el archivo dating/Settings.py de nuestro proyecto, modificar:
```
DATABASES = {
   	'default': {
     		'ENGINE': 'django.db.backends.postgresql_psycopg2',
       		'NAME': 'dating',
       		'USER': 'siteadmin',
       		'PASSWORD': '@dm!n',
        	'HOST': 'localhost',
        	'PORT': '5432',
		'OPTIONS': {
			    'options': '-c search_path=dating'
			}
   		}
	}
```
- Aplicar las migraciones
	* ` $ python manage.py makemigrations `
	* ` $ python manage.py migrate `


######  Editar

- En la tabla `auth_user ` columna `username` valor  `lenght = 254`
