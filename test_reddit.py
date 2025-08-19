import requests
import requests.auth
import time


# --- 🔑 A RELLENAR POR EL USUARIO ---
# 1. Ve a https://www.reddit.com/prefs/apps
# 2. Crea una nueva app de tipo "script".
# 3. Copia el ID personal y el secreto aquí.

CLIENT_ID = "n62UfVfVlmYuShe_qTSwkA"
CLIENT_SECRET = "jE_P96qMLNfEt5ZzbvP729qFqV-cnA"

# 4. Pon tu nombre de usuario de Reddit para el User-Agent.
#    Reddit requiere un User-Agent único para evitar bloqueos.
USER_AGENT = "PruebaAPI/0.1 by u/SoupDependent2943"

# --- FIN DE LA CONFIGURACIÓN ---


def probar_api_reddit():
    """
    Intenta autenticarse y hacer una petición simple a la API de Reddit.
    """
    print("Intentando obtener un token de acceso de Reddit...")

    # Paso 1: Autenticarse para obtener un token de acceso
    try:
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        data = {
            'grant_type': 'client_credentials',
        }
        headers = {'User-Agent': USER_AGENT}

        res = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            auth=auth,
            data=data,
            headers=headers
        )

        # Si la autenticación falla, res.raise_for_status() lanzará un error
        res.raise_for_status()
        
        access_token = res.json()['access_token']
        print("✅ Token de acceso obtenido con éxito.")

    except requests.exceptions.HTTPError as err:
        print(f"❌ Error al autenticarse. Revisa tu CLIENT_ID y CLIENT_SECRET.")
        print(f"   Detalle del error: {err.response.status_code} - {err.response.text}")
        return

    # Paso 2: Usar el token para hacer una petición a la API
    print("Usando el token para pedir los posts más populares de r/learnpython...")
    headers['Authorization'] = f'bearer {access_token}'

    try:
        api_res = requests.get(
            'https://oauth.reddit.com/r/learnpython/hot',
            headers=headers,
            params={'limit': 1} # Solo pedimos 1 post para que sea rápido
        )
        api_res.raise_for_status()

        # Si todo fue bien, imprimimos un mensaje de éxito
        print("\n🚀 ¡TODO FUNCIONA PERFECTAMENTE!")
        print("   Se pudo conectar y traer datos de Reddit sin problemas.")

    except requests.exceptions.HTTPError as err:
        print(f"❌ Falló la petición a la API, aunque el token era válido.")
        print(f"   Detalle del error: {err.response.status_code} - {err.response.text}")


if __name__ == '__main__':
    if "TU_CLIENT_ID_VA_AQUI" in CLIENT_ID or "TU_NOMBRE_DE_USUARIO" in USER_AGENT:
        print("⚠️ ¡Atención! Debes rellenar las variables CLIENT_ID, CLIENT_SECRET y USER_AGENT en el script.")
    else:
        probar_api_reddit()

# Bucle infinito para pedir datos constantemente
while True:
    print("Buscando nuevos posts...")
    api_res = requests.get('https://oauth.reddit.com/r/learnpython/new', headers=headers, params={'limit': 1})
    
    if api_res.status_code == 200:
        # Extrae el post más nuevo
        latest_post = api_res.json()['data']['children'][0]['data']
        print(f"  Último post: {latest_post['title']}")
    
    # Espera 10 segundos antes de volver a preguntar
    time.sleep(10)