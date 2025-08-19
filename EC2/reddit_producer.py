import praw
import psycopg2
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- CONFIGURACIÓN ---
REDDIT_CLIENT_ID = "CLIENT_ID_DE_REDDIT"
REDDIT_CLIENT_SECRET = "CLIENT_SECRET_DE_REDDIT"
REDDIT_USER_AGENT = "GamingSentimentTracker/0.1 by u/USUARIO_REDDIT"

DB_ENDPOINT = "ENDPOINT_DE_RDS"
DB_NAME = "postgres"
DB_USER = "TUSUARIO_MAESTRO"
DB_PASSWORD = "CONTRASEÑA_SEGURA"

# Lista de palabras clave que queremos rastrear
KEYWORDS = {
    'Juego': ['Starfield', 'Helldivers 2', 'Elden Ring', 'GTA VI', 'Baldur\'s Gate 3', 'Palworld'],
    'Consola': ['PS5', 'Xbox', 'Nintendo Switch', 'PlayStation 5'],
    'Plataforma': ['PC', 'Steam'],
    'Empresa': ['Ubisoft', 'Nintendo', 'Sony', 'FromSoftware']
}
# --- FIN DE LA CONFIGURACIÓN ---

def analyze_sentiment(text):
    """Analiza el sentimiento de un texto y devuelve 'positive', 'negative' o 'neutral'."""
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    
    compound_score = score['compound']
    if compound_score >= 0.05:
        return 'positive', compound_score
    elif compound_score <= -0.05:
        return 'negative', compound_score
    else:
        return 'neutral', compound_score

def find_keyword(text):
    """Busca una palabra clave en el texto y devuelve la entidad y su tipo."""
    for entity_type, keywords_list in KEYWORDS.items():
        for keyword in keywords_list:
            if keyword.lower() in text.lower():
                return keyword, entity_type
    return None, None

def connect_to_database():
    try:
        conn = psycopg2.connect(
            host=DB_ENDPOINT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def main():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT
    )
    conn = connect_to_database()
    if not conn:
        return

    subreddit = reddit.subreddit("gaming")
    print(f"Empezando a monitorear y analizar comentarios en r/{subreddit.display_name}...")

    try:
        for comment in subreddit.stream.comments(skip_existing=True):
            try:
                keyword, entity_type = find_keyword(comment.body)
                
                if keyword:
                    sentiment_label, sentiment_score = analyze_sentiment(comment.body)
                    
                    print(f"Mención encontrada: '{keyword}' | Sentimiento: {sentiment_label.upper()} ({sentiment_score})")

                    sql_insert = """
                        INSERT INTO game_mentions (timestamp, entity_mentioned, entity_type, sentiment_score, sentiment_label, context_url)
                        VALUES (to_timestamp(%s), %s, %s, %s, %s, %s)
                        ON CONFLICT (context_url) DO NOTHING;
                    """
                    data_to_insert = (
                        comment.created_utc,
                        keyword,
                        entity_type,
                        sentiment_score,
                        sentiment_label,
                        f"https://www.reddit.com{comment.permalink}"
                    )
                    
                    with conn.cursor() as cur:
                        cur.execute(sql_insert, data_to_insert)
                    conn.commit()

            except Exception as e:
                print(f"Error procesando el comentario {comment.id}: {e}")
                conn.rollback()

    except KeyboardInterrupt:
        print("\nProceso detenido.")
    except Exception as e:
        print(f"Error crítico en el stream: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    main()