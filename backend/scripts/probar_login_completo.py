import httpx
from sqlmodel import Session, create_engine

import app.crud as crud
from app.core.config import settings

motor = create_engine(str(settings.DATABASE_URL))

# 1. Probar authenticate en crud
print("1. Probando crud.authenticate con credenciales maestras...")
with Session(motor) as sesion:
    usuario = crud.authenticate(
        session=sesion, email="admin@proteccioncivil.gob.mx", password="Admin1234!"
    )
    if usuario:
        print("   AUTENTICACION EXITOSA EN CRUD:")
        print("   Nombre:", usuario.full_name)
        print("   Correo:", usuario.email)
        print("   Rol:", usuario.rol)
        print("   Superuser:", usuario.is_superuser)
    else:
        print("   FALLO EN AUTENTICACION DE CRUD")

# 2. Probar endpoint HTTP local /api/v1/login/access-token
print("\n2. Probando endpoint HTTP local /api/v1/login/access-token...")
try:
    with httpx.Client(timeout=10.0) as cliente:
        res = cliente.post(
            "http://127.0.0.1:8000/api/v1/login/access-token",
            data={"username": "admin@proteccioncivil.gob.mx", "password": "Admin1234!"},
        )
        print("   Status Login HTTP:", res.status_code)
        if res.status_code == 200:
            datos_token = res.json()
            print("   Token recibido exitosamente!")
            print("   Tipo de token:", datos_token.get("token_type"))
            print(
                "   Primeros 20 caracteres:",
                datos_token.get("access_token", "")[:20] + "...",
            )
        else:
            print("   Error en login HTTP:", res.text)
except Exception as e:
    print("   Excepcion en peticion HTTP:", e)

# 3. Probar endpoint HTTP a traves del nuevo tunel de Cloudflare
print("\n3. Probando endpoint HTTP a traves del nuevo tunel de Cloudflare...")
url_tunel = "https://buddy-week-great-flip.trycloudflare.com"
try:
    with httpx.Client(timeout=15.0) as cliente:
        res = cliente.post(
            f"{url_tunel}/api/v1/login/access-token",
            data={"username": "admin@proteccioncivil.gob.mx", "password": "Admin1234!"},
        )
        print("   Status Login Cloudflare:", res.status_code)
        if res.status_code == 200:
            datos_token = res.json()
            print("   Token recibido exitosamente por Cloudflare!")
            print("   Tipo de token:", datos_token.get("token_type"))
        else:
            print("   Error en login Cloudflare:", res.text)
except Exception as e:
    print("   Excepcion en peticion Cloudflare:", e)
