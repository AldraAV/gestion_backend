import urllib.request
import urllib.parse
import json

base_url = "http://127.0.0.1:8000"

# 1. Login admin
datos_login = urllib.parse.urlencode({
    "username": "admin@proteccioncivil.gob.mx",
    "password": "Admin1234!"
}).encode("utf-8")

req_login = urllib.request.Request(
    f"{base_url}/api/v1/login/access-token",
    data=datos_login,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

with urllib.request.urlopen(req_login) as resp:
    res_login = json.loads(resp.read().decode("utf-8"))
    token = res_login["access_token"]
    print("Token obtenido con exito.")

# 2. Consultar mi-albergue
req_albergue = urllib.request.Request(
    f"{base_url}/api/v1/albergues/mi-albergue",
    headers={"Authorization": f"Bearer {token}"}
)

with urllib.request.urlopen(req_albergue) as resp:
    res_albergue = json.loads(resp.read().decode("utf-8"))
    print("\n--- RESPUESTA DE MI-ALBERGUE PARA ADMIN ---")
    print("Albergue ID:", res_albergue.get("albergue_id"))
    print("Nombre:", res_albergue.get("nombre"))
    print("Administrador a Cargo:", json.dumps(res_albergue.get("administrador_a_cargo"), indent=2))
    print("Capacidad Maxima:", res_albergue.get("infraestructura", {}).get("capacidad_maxima"))
    print("Ocupacion Actual:", res_albergue.get("infraestructura", {}).get("ocupacion_actual"))
    print("Total Personas Albergadas:", res_albergue.get("total_personas_registradas"))
    print("Primeras 2 personas:", [p["nombre_completo"] for p in res_albergue.get("personas_albergadas", [])[:2]])
