import psycopg2

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_ENDPOINT = "ENDPOINT_DE_RDS"
DB_NAME = "postgres"
DB_USER = "USUARIO_MAESTRO"
DB_PASSWORD = "CONTRASEÑA_SEGURA"
# --- FIN DE LA CONFIGURACIÓN ---

def initialize_database_schema():
    """
    Se conecta a la base de datos para crear y/o actualizar el esquema.
    - Crea la tabla 'game_mentions' si no existe.
    - Añade columnas adicionales si no existen.
    """
    conn = None
    try:
        print("Conectando a la base de datos PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_ENDPOINT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        # --- 1. Crear la tabla principal ---
        print("Paso 1: Creando la tabla 'game_mentions' si no existe...")
        create_table_script = '''
            CREATE TABLE IF NOT EXISTS game_mentions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                entity_mentioned VARCHAR(100) NOT NULL,
                entity_type VARCHAR(50),
                sentiment_score FLOAT,
                context_url VARCHAR(255) UNIQUE
            );
        '''
        cur.execute(create_table_script)
        print("-> Tabla principal verificada/creada.")

        # Añadir columnas adicionales ---
        print("Paso 2: Asegurando que la columna 'sentiment_label' exista...")
        alter_table_script = '''
            ALTER TABLE game_mentions
            ADD COLUMN IF NOT EXISTS sentiment_label VARCHAR(10);
        '''
        cur.execute(alter_table_script)
        print("-> Columna 'sentiment_label' verificada/añadida.")
        
        # Confirma todos los cambios en la base de datos
        conn.commit()
        
        print("\n¡Esquema de la base de datos inicializado con éxito!")
        
        # Cierra la comunicación
        cur.close()

    except Exception as e:
        print(f"Error durante la inicialización de la base de datos: {e}")
        if conn:
            conn.rollback() # Revierte los cambios si algo falló
    finally:
        if conn is not None:
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == '__main__':
    initialize_database_schema()