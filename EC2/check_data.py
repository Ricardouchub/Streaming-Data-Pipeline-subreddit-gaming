import psycopg2

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_ENDPOINT = "ENDPOINT_DE_RDS"
DB_NAME = "postgres"
DB_USER = "USUARIO_MAESTRO"
DB_PASSWORD = "CONTRASEÑA_SEGURA"
# --- FIN DE LA CONFIGURACIÓN ---

def check_database_content():
    """Se conecta a la BD y muestra los últimos 10 registros."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_ENDPOINT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM game_mentions;")
        count = cur.fetchone()[0]
        print(f"\nTotal de comentarios en la tabla: {count}\n")

        print("--- Mostrando los últimos 10 comentarios guardados ---")
        cur.execute("SELECT timestamp, entity_mentioned, sentiment_label FROM game_mentions ORDER BY timestamp DESC LIMIT 10;")
        
        results = cur.fetchall()
        for row in results:
            print(f"Fecha: {row[0]} | Entidad: {row[1]} | Sentimiento: {row[2]}")

        cur.close()

    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    check_database_content()