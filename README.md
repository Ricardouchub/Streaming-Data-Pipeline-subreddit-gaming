# Pipeline de Datos en Tiempo Real y Análisis de Sentimiento para r/gaming en AWS

Este proyecto implementa un pipeline de datos en tiempo real que recolecta comentarios del subreddit `r/gaming`, realiza análisis de sentimiento sobre entidades específicas como algunos juegos, consolas y empresas, y almacena los resultados en una base de datos en la nube de AWS. Los datos son visualizados a través de un dashboard interactivo, alojado en el mismo servidor y accesible públicamente a través de la web.

<img width="739" height="594" alt="image" src="https://github.com/user-attachments/assets/14611ed5-3cd3-4670-8bcd-50976d7179b6" />



---

## Características Principales

-   **Recolección en Tiempo Real:** Un script de Python se ejecuta 24/7 en un servidor **AWS EC2**, escuchando el flujo de nuevos comentarios de `r/gaming`.
-   **Procesamiento y Análisis de Sentimiento:** Utiliza NLP con la librería **VADER** para detectar palabras clave y clasificar el sentimiento de cada comentario relevante como positivo, negativo o neutral.
-   **Almacenamiento Seguro:** Los datos procesados se guardan en una base de datos PostgreSQL gestionada por **Amazon RDS**, la cual reside en una red privada y segura.
-   **Visualización Web Pública:** Un dashboard interactivo construido con **Plotly Dash** se ejecuta en el mismo servidor EC2, permitiendo la exploración y visualización de los datos desde cualquier navegador web.
  
---

## Arquitectura

El pipeline sigue un flujo de datos claro desde la recolección hasta la visualización:

1.  **Servicio de Recolección:** Un script (`reddit_producer.py`) se ejecuta como un servicio `systemd` permanente en **Amazon EC2**.
2.  **Extracción:** El servicio se conecta a la API de Reddit y monitorea en tiempo real los nuevos comentarios.
3.  **Transformación y Enriquecimiento:**
    -   Cada comentario es analizado para buscar menciones de entidades clave.
    -   Si se encuentra una mención, se calcula una puntuación y etiqueta de sentimiento.
4.  **Carga:**
    -   El script se conecta a la base de datos **Amazon RDS (PostgreSQL)** a través de la red privada de la VPC.
    -   Inserta una nueva fila en la tabla `game_mentions` con los datos enriquecidos.
5.  **Visualización y Acceso:**
    -   **Dashboard Público:** La aplicación de dashboard (`dashboard_app.py`) también se ejecuta en el servidor **EC2**. Se conecta internamente a la base de datos y es accesible públicamente a través de la IP del servidor en el puerto 8050.
    -   **Administración Segura:** Para tareas de administración de la base de datos, se utiliza un **Túnel SSH** a través de la instancia EC2 para conectar de forma segura con herramientas como **DBeaver**.
    

---

## Herramientas y Servicios Utilizados

-   **Amazon EC2:** Servidor virtual en la nube que aloja y ejecuta el script de recolección de datos 24/7.
-   **Amazon RDS (PostgreSQL):** Base de datos relacional gestionada que provee almacenamiento persistente y escalable.
-   **Amazon VPC:** Red virtual privada que aísla los recursos de AWS, garantizando una comunicación interna segura.
-   **Python 3:** Lenguaje principal para todo el proyecto.
    -   **Librerías del Colector:** `praw`, `psycopg2-binary`, `vaderSentiment`.
    -   **Librerías del Dashboard:** `dash`, `dash-bootstrap-components`, `plotly`, `pandas`, `SQLAlchemy`, `python-dotenv`.
-   **DBeaver:** Cliente de base de datos.

---

## Estructura del Repositorio


* **/EC2/**
  * `reddit_producer.py`: El script principal que se ejecuta en la instancia EC2.
  * `setup_database.py`: Script de utilidad para crear y configurar el esquema de la base de datos.
  * `requirements-producer.txt`: Dependencias para el script recolector en EC2.

* **/main/**
  * `dashboard_app.py`: La aplicación de Plotly Dash que se ejecuta localmente.
  * `requirements-dashboard.txt`: Dependencias para ejecutar el dashboard localmente.
  * `.env.example`: Plantilla para el archivo de configuración local del dashboard.

---

## Configuración y Despliegue del Proyecto

#### 1. Configuración en AWS
-   Lanzar una instancia **EC2** (ej. `t2.micro` con Ubuntu).
-   Crear una base de datos **RDS PostgreSQL** (ej. `db.t2.micro`).
-   Configurar los **Grupos de Seguridad** para permitir:
    -   Acceso **SSH (puerto 22)** a la instancia EC2 desde tu IP.
    -   Acceso **HTTP (puerto 8050)** al dashboard en EC2 desde cualquier IP (`0.0.0.0/0`).
    -   Acceso **PostgreSQL (puerto 5432)** a la instancia RDS desde el grupo de seguridad de la instancia EC2.

#### 2. Despliegue en la Instancia EC2
1.  Clonar el repositorio en la instancia EC2.
2.  Crear un entorno virtual e instalar todas las dependencias: `pip install -r requirements-producer.txt -r requirements-dashboard.txt`.
3.  Transferir los archivos del dashboard (`dashboard_app.py` y la carpeta `assets`) al servidor usando `scp`.
4.  Configurar las credenciales en los scripts y crear un archivo `.env` en el servidor para el dashboard.
5.  Ejecutar `python initialize_database.py` para crear la tabla.
6.  Crear y activar el servicio `systemd` para `reddit_producer.py`.
7.  Ejecutar el dashboard en segundo plano: `nohup python dashboard_app.py &`.

 #### 3. Acceso al Dashboard
-   Abre un navegador y ve a `http://<IP_PUBLICA_EC2>:8050`.

---

## Resultado
El resultado final es un pipeline de datos completamente funcional que alimenta un dashboard interactivo, permitiendo el análisis de la opinión pública en la comunidad de gaming.

### Vista del Dashboard 
<img width="2558" height="1233" alt="image" src="https://github.com/user-attachments/assets/ea7b09f4-2a9b-40e4-9539-3bf9ddb43266" />



### Vista de la Base de Datos en DBeaver
<img width="1554" height="972" alt="image" src="https://github.com/user-attachments/assets/7e23508f-3572-48ea-90b9-3b909ac2de8c" />


---

## Autor

**Ricardo Urdaneta**

**[LinkedIn](https://www.linkedin.com/in/ricardourdanetacastro)** | **[GitHub](https://github.com/Ricardouchub)**
