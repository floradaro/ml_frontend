# Autenticación con Flask y Keycloak

Aplicación de que integra Flask con Keycloak para autenticación y autorización usando OpenID Connect.

## Requisitos previos

- Python 3.7+
- Keycloak ejecutándose localmente
- Pip para gestionar dependencias

## Configuración inicial

1. Clona los repositorio o descarga los archivos -> Repositorio keycloak : https://github.com/floradaro/ml_keycloak

2. Crea un entorno virtual (recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Configuración inicial

Instala los requerimientos con:

```bash
pip install -r requirements.txt
```

## Ejecución de la aplicación

Inicia el servidor Flask con:

```bash
python app.py
```

# Desde docker Desktop

## Para levantar el contenendor

Estando dentro del directorio

```bash
docker build -t flask-frontend .
docker run -d -p 5000:5000 --name flask-frontend flask-frontend
```
## Proba en el navegador

Abrí en el navegador:
👉 http://localhost:5000
Deberías ser redirigido al login de Keycloak y luego ver los botones según tus roles.