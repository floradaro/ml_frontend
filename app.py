from flask import Flask, redirect, request, session, url_for, render_template, flash
from keycloak import KeycloakOpenID
import requests
import os

app = Flask(__name__)
app.secret_key = "clave-secreta"

# Configuración de Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="http://host.docker.internal:8081/",
    client_id="frontend-client",
    realm_name="ml",
)

REDIRECT_URI = "http://localhost:5000/callback"

@app.route("/")
def home():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("login"))
    
    userinfo = session.get("userinfo", {})
    roles = userinfo.get("resource_access", {}).get("frontend-client", {}).get("roles", [])
    
    return render_template("index.html", roles=roles)

@app.route("/login")
def login():
    auth_url = keycloak_openid.auth_url(
        redirect_uri=REDIRECT_URI,
        scope="openid profile email"  # Asegúrate de incluir los scopes necesarios
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        flash("Error: No se recibió el código de autorización")
        return redirect(url_for("login"))

    try:
        token = keycloak_openid.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=REDIRECT_URI
        )
        
        access_token = token.get("access_token")
        session["access_token"] = token.get("access_token")
        session["refresh_token"] = token.get("refresh_token")
        
        # Decodificar el token para obtener los roles sin usar userinfo
        from jwt import decode  # pip install pyjwt
        decoded_token = decode(access_token, options={"verify_signature": False})
        session["userinfo"] = {
            "resource_access": {
                "frontend-client": {
                    "roles": decoded_token.get("resource_access", {}).get("frontend-client", {}).get("roles", [])
                }
            }
        }
        
        return redirect(url_for("home"))
    
    except Exception as e:
        flash(f"Error de autenticación: {str(e)}")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    # Obtener tokens antes de limpiar la sesión
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    
    # Limpiar la sesión local primero
    session.clear()
    
    try:
        # Hacer logout en Keycloak si tenemos tokens
        if refresh_token:
            keycloak_openid.logout(refresh_token)
        
        # Construir URL de logout completa
        logout_url = (
            f"{keycloak_openid.server_url}realms/{keycloak_openid.realm_name}/"
            f"protocol/openid-connect/logout?"
            f"post_logout_redirect_uri={url_for('login', _external=True)}"
        )
        
        # Si tenemos access_token, añadirlo como hint
        if access_token:
            logout_url += f"&id_token_hint={access_token}"
        
        return redirect(logout_url)
        
    except Exception as e:
        print(f"Error en logout: {str(e)}")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
