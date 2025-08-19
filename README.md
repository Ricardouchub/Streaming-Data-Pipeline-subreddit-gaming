# Data Streaming Pipeline y Análisis de Sentimiento para r/gaming en AWS

Este proyecto implementa un pipeline de datos en tiempo real que recolecta comentarios del subreddit `r/gaming`, realiza análisis de sentimiento sobre entidades específicas como algunos juegos, consolas y empresas, y almacena los resultados en una base de datos en la nube de AWS. Los datos son visualizados a través de un dashboard interactivo que se ejecuta de manera local.


<img width="610" height="512" alt="image" src="https://github.com/user-attachments/assets/da195a9f-a43c-44c3-a584-8c30c65d52fe" />


---

## Características Principales

-   **Recolección a Tiempo Real:** Un script de Python se ejecuta 24/7 en un servidor de AWS **EC2**, escuchando el flujo de nuevos comentarios del subreddit `r/gaming` a través de la API de Reddit.
-   **Procesamiento y Análisis de Sentimiento:** Utiliza Procesamiento de Lenguaje Natural (NLP) con la librería **VADER** para detectar palabras clave predefinidas y clasificar el sentimiento de cada comentario relevante como positivo, negativo o neutral.
-   **Almacenamiento:** Los datos procesados se guardan en una base de datos PostgreSQL gestionada por **Amazon RDS**, la cual reside en una red privada y segura.
-   **Visualización Interactiva Local:** Un dashboard construido con Plotly Dash se conecta de forma segura a la base de datos en la nube a través de un túnel SSH, permitiendo la exploración y visualización de los datos sin exponer la base de datos a internet.
  
---

## Arquitectura

El pipeline sigue un flujo de datos claro desde la recolección hasta la visualización:

1.  **Servicio de Recolección:** Un script de Python (`reddit_producer.py`) se ejecuta como un servicio `systemd` permanente en una instancia **Amazon EC2**.
2.  **Extracción:** El servicio se conecta a la API de Reddit usando la librería `praw` y monitorea en tiempo real los nuevos comentarios publicados en el subreddit `r/gaming`.
3.  **Transformación y Enriquecimiento:**
    -   Cada comentario es analizado para buscar menciones de entidades clave (juegos, consolas, empresas).
    -   Si se encuentra una mención, la librería `vaderSentiment` analiza el texto completo del comentario para calcular una puntuación y una etiqueta de sentimiento (positivo, negativo, neutral).
4.  **Carga:**
    -   El script se conecta a la base de datos **Amazon RDS (PostgreSQL)**. Esta conexión es segura ya que tanto EC2 como RDS están en la misma red privada (VPC).
    -   Inserta una nueva fila en la tabla `game_mentions` con los datos enriquecidos: timestamp, entidad mencionada, tipo de entidad, sentimiento y un enlace al comentario original.
5.  **Visualización Segura:**
    -   En la máquina local del usuario, un **Túnel SSH** se establece con el servidor EC2.
    -   La aplicación de dashboard (`dashboard_app.py`), construida con **Plotly Dash**, se conecta a la base de datos a través de este túnel, apuntando a `localhost`. Esto permite que el dashboard lea los datos de forma segura sin que la base de datos esté expuesta públicamente.

---

## Herramientas y Servicios Utilizados

-   **Amazon EC2:** Servidor virtual en la nube que aloja y ejecuta el script de recolección de datos 24/7.
-   **Amazon RDS (PostgreSQL):** Base de datos relacional gestionada que provee almacenamiento persistente y escalable.
-   **Amazon VPC:** Red virtual privada que aísla los recursos de AWS, garantizando una comunicación interna segura.
-   **`systemd`:** Gestor de servicios de Linux utilizado para asegurar que el script de recolección se ejecute de forma permanente y se reinicie automáticamente en caso de fallo.
-   **Python 3:** Lenguaje principal para todo el proyecto.
    -   **Librerías del Colector:** `praw`, `psycopg2-binary`, `vaderSentiment`.
    -   **Librerías del Dashboard:** `dash`, `dash-bootstrap-components`, `plotly`, `pandas`, `SQLAlchemy`, `python-dotenv`.
-   **DBeaver:** Cliente de base de datos utilizado para la gestión y verificación de datos a través del túnel SSH.

---

## Estructura del Repositorio



-   **`reddit_producer.py`**: El script principal que se ejecuta en la instancia EC2.
-   **`dashboard_app.py`**: La aplicación de Plotly Dash que se ejecuta localmente.
-   **`initialize_database.py`**: Script de utilidad para crear y configurar el esquema de la base de datos.
-   **`requirements-producer.txt`**: Dependencias para el script recolector en EC2.
-   **`requirements-dashboard.txt`**: Dependencias para ejecutar el dashboard localmente.
-   **`.env.example`**: Plantilla para el archivo de configuración local del dashboard.

---

## Configuración y Despliegue del Proyecto

#### 1. Configuración en AWS
-   Lanzar una instancia **EC2** (ej. `t2.micro` con Ubuntu).
-   Crear una base de datos **RDS PostgreSQL** (ej. `db.t2.micro`).
-   Configurar los **Grupos de Seguridad** para permitir:
    -   Acceso **SSH (puerto 22)** a la instancia EC2 desde tu IP.
    -   Acceso **PostgreSQL (puerto 5432)** a la instancia RDS desde el grupo de seguridad de la instancia EC2.

#### 2. Despliegue del Colector (en la instancia EC2)
1.  Clonar el repositorio en la instancia EC2.
2.  Crear un entorno virtual de Python e instalar las dependencias: `pip install -r requirements-producer.txt`.
3.  Configurar las credenciales en los scripts (o usar variables de entorno).
4.  Ejecutar `python initialize_database.py` para crear la tabla.
5.  Crear el archivo de servicio `reddit_producer.service` en `/etc/systemd/system/`.
6.  Activar e iniciar el servicio: `sudo systemctl daemon-reload`, `sudo systemctl start reddit_producer`, `sudo systemctl enable reddit_producer`.

#### 3. Ejecución del Dashboard (en tu PC local)
1.  Clonar el repositorio en tu PC.
2.  Instalar las dependencias: `pip install -r requirements-dashboard.txt`.
3.  Crear un archivo `.env` a partir de `.env.example` y rellenarlo con tus credenciales.
4.  En una terminal, iniciar el **Túnel SSH** a tu instancia EC2.
5.  En otra terminal, ejecutar la aplicación del dashboard: `python dashboard_app.py`.

---

## Resultado
El resultado final es un pipeline de datos completamente funcional que alimenta un dashboard interactivo, permitiendo el análisis de la opinión pública en la comunidad de gaming.

### Vista del Dashboard 
<img width="2555" height="1205" alt="image" src="https://github.com/user-attachments/assets/2459535c-6695-418f-af77-931d467e6f0c" />

### Vista de la Base de Datos en DBeaver
<img width="1554" height="972" alt="image" src="https://github.com/user-attachments/assets/7e23508f-3572-48ea-90b9-3b909ac2de8c" />

### Logs del Servicio en EC2 mostrando recolección en tiempo real
![Logs del Servicio en EC2](URL_DE_TU_IMAGEN_DE_LOS_LOGS_AQUI)

---

## Autor

**Ricardo Urdaneta**

**[LinkedIn](https://www.linkedin.com/in/ricardourdanetacastro)** | **[GitHub](https://github.com/Ricardouchub)**
