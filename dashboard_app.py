# dashboard_app.py

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import date, timedelta

# --- CONFIGURACIÓN E INICIALIZACIÓN ---

load_dotenv()

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
                title='Sentimiento en r/gaming')
server = app.server

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

KEYWORDS = {
    'Juego': ['RuneScape', 'Marvel Rivals', 'Elden Ring', 'Overwatch', 'League of Legends', 'World of Warcraft', 'Expedition 33', 'Resident Evil', 'Silent Hill', 'Death Stranding'],
    'Consola': ['PS5', 'Xbox', 'Nintendo Switch'],
    'Empresa': ['Ubisoft', 'Nintendo', 'Sony', 'FromSoftware', 'EA', 'Blizzard', 'Riot', 'Epic Games', 'Bethesda', 'Square Enix']
}

SENTIMENT_COLORS = {'positive': '#198754', 'negative': '#DC3545', 'neutral': '#6C757D'}

# --- FUNCIÓN DE DATOS ---

def query_data(start_date, end_date):
    try:
        db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_url)
        end_date_inclusive = pd.to_datetime(end_date) + timedelta(days=1)
        sql_query = """
            SELECT timestamp, entity_mentioned, entity_type, sentiment_label
            FROM game_mentions
            WHERE timestamp BETWEEN %(start)s AND %(end)s;
        """
        df = pd.read_sql_query(sql_query, engine, params={'start': start_date, 'end': end_date_inclusive})
        return df
    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        return pd.DataFrame(columns=['timestamp', 'entity_mentioned', 'entity_type', 'sentiment_label'])

# ---  LAYOUT ---

header = dbc.Navbar(
    dbc.Container([
        dbc.Row(
            [
                dbc.Col(md=4),
                dbc.Col(html.Img(src=app.get_asset_url('img/banner.png'), height="100px"), md=4, className="text-center"),
                dbc.Col(dbc.Button(html.I(className="bi bi-filter-right"), id="btn-toggle", color="primary", outline=True), md=4, className="d-flex justify-content-end align-items-center"),
            ],
            align="center", className="w-100"
        )
    ], fluid=True),
    color='black', dark=True, className='shadow-sm sticky-top border-bottom border-primary py-2'
)

footer_layout = html.Div([
    html.Hr(className="my-3"),
    html.P("Realizado por: Ricardo Urdaneta", className="text-muted small"),
    dbc.Row([
        dbc.Col(html.A(dbc.Button([html.I(className="bi bi-github me-2"), "GitHub"], color="secondary", outline=True, className="w-100"), href="https://github.com/Ricardouchub", target="_blank"), width=6),
        dbc.Col(html.A(dbc.Button([html.I(className="bi bi-linkedin me-2"), "LinkedIn"], color="secondary", outline=True, className="w-100"), href="https://www.linkedin.com/in/ricardourdanetacastro", target="_blank"), width=6)
    ])
], className="mt-auto")

sidebar = dbc.Collapse(
    dbc.Card(
        dbc.CardBody([
            html.Div([
                html.P("Este dashboard analiza en tiempo real los comentarios del subreddit r/gaming para medir el sentimiento de la comunidad sobre juegos, consolas y empresas.", className="small text-light"),
                html.P("Utilice los filtros para explorar los datos por fecha o entidad específica.", className="small text-secondary")
            ]),
            html.Hr(),
            html.H5('🎯 Filtros', className='fw-bold mb-3 text-primary'),
            dbc.Form([
                dbc.Label('Rango de Fechas', className='fw-semibold small text-white'),
                dcc.DatePickerRange(id='date-picker-range', min_date_allowed=date(2024, 1, 1), max_date_allowed=date.today() + timedelta(days=1), start_date=date.today() - timedelta(days=3), end_date=date.today(), display_format='YYYY-MM-DD', className='mb-3 w-100'),
                dbc.Label('Juego', className='fw-semibold small text-white'),
                dcc.Dropdown(id='game-filter', options=[{'label': 'Todos', 'value': 'All'}] + [{'label': g, 'value': g} for g in KEYWORDS['Juego']], value='All', className='mb-3'),
                dbc.Label('Consola', className='fw-semibold small text-white'),
                dcc.Dropdown(id='console-filter', options=[{'label': 'Todas', 'value': 'All'}] + [{'label': c, 'value': c} for c in KEYWORDS['Consola']], value='All', className='mb-3'),
                dbc.Label('Empresa', className='fw-semibold small text-white'),
                dcc.Dropdown(id='company-filter', options=[{'label': 'Todas', 'value': 'All'}] + [{'label': e, 'value': e} for e in KEYWORDS['Empresa']], value='All', className='mb-3'),
                dbc.Button([html.I(className="bi bi-download me-2"), "Descargar CSV"], id="btn-download", color="primary", outline=True, className="w-100"),
                dcc.Download(id="download-csv")
            ]),
            footer_layout
        ], className="d-flex flex-column h-100 p-3"),
        className='shadow-sm h-100 bg-black text-light border-0',
    ),
    id="collapse-sidebar",
    is_open=True
)

def kpi_card(title, kpi_id, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.Small(title, className="fw-semibold text-muted"),
            html.H4(id=kpi_id, className=f"text-{color} fw-bold mb-0")
        ]),
        className="shadow-sm rounded-3 border-0 text-center bg-black"
    )

kpi_cards = dbc.Row([
    dbc.Col(kpi_card("Total Menciones", "kpi-total-mentions", "info"), md=3),
    dbc.Col(kpi_card("Sentimiento Positivo", "kpi-positive-pct", "success"), md=3),
    dbc.Col(kpi_card("Entidad más Mencionada", "kpi-top-entity", "warning"), md=3),
    dbc.Col(kpi_card("Sentimiento General", "kpi-overall-sentiment", "primary"), md=3),
], className="mb-4 g-3")

app.layout = dbc.Container([
    header,
    dbc.Row([
        dbc.Col(id="main-content", children=[
            kpi_cards,
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(dcc.Loading(dcc.Graph(id='sentiment-history-chart'))), className="shadow-sm rounded-3 border-0 bg-black"), className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(dcc.Loading(dcc.Graph(id='sentiment-pie-chart'))), className="shadow-sm rounded-3 border-0 bg-black"), md=4, className="mb-4"),
                dbc.Col(dbc.Card(dbc.CardBody(dcc.Loading(dcc.Graph(id='top-entities-chart'))), className="shadow-sm rounded-3 border-0 bg-black"), md=8, className="mb-4"),
            ]),
        ]),
        dbc.Col(sidebar, id="sidebar-col", width=2),
    ], className="mt-3"),
    dcc.Interval(id='interval-component', interval=5 * 60 * 1000, n_intervals=0)
], fluid=True, className="dbc")

# --- CALLBACKS ---

@app.callback(
    [Output("collapse-sidebar", "is_open"),
     Output("main-content", "width"),
     Output("sidebar-col", "className")],
    [Input("btn-toggle", "n_clicks")],
    [State("collapse-sidebar", "is_open")],
)
def toggle_sidebar(n, is_open):
    if n:
        if is_open:
            return False, 12, "d-none"
        else:
            return True, 10, ""
    return is_open, 10, ""

@app.callback(
    Output("download-csv", "data"),
    [Input("btn-download", "n_clicks")],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('game-filter', 'value'),
     State('console-filter', 'value'),
     State('company-filter', 'value')],
    prevent_initial_call=True,
)
def download_filtered_data(n, start_date, end_date, selected_game, selected_console, selected_company):
    df = query_data(start_date, end_date)
    if df.empty:
        return None
    
    dff = df.copy()
    if selected_game != 'All': dff = dff[dff['entity_mentioned'] == selected_game]
    if selected_console != 'All': dff = dff[dff['entity_mentioned'] == selected_console]
    if selected_company != 'All': dff = dff[dff['entity_mentioned'] == selected_company]
    
    return dcc.send_data_frame(dff.to_csv, "sentiment_data_filtered.csv", index=False)

@app.callback(
    [Output('kpi-total-mentions', 'children'),
     Output('kpi-positive-pct', 'children'),
     Output('kpi-top-entity', 'children'),
     Output('kpi-overall-sentiment', 'children'),
     Output('sentiment-history-chart', 'figure'),
     Output('sentiment-pie-chart', 'figure'),
     Output('top-entities-chart', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('game-filter', 'value'),
     Input('console-filter', 'value'),
     Input('company-filter', 'value')]
)
def update_dashboard(n, start_date, end_date, selected_game, selected_console, selected_company):
    df = query_data(start_date, end_date)

    if df.empty:
        empty_fig = go.Figure().update_layout(title_text='No hay datos para la selección actual', template='plotly_dark', paper_bgcolor='black', plot_bgcolor='black')
        return "0", "0%", "N/A", "N/A", empty_fig, empty_fig, empty_fig

    top_entities_df = df.copy()

    dff = df.copy()
    if selected_game != 'All': dff = dff[dff['entity_mentioned'] == selected_game]
    if selected_console != 'All': dff = dff[dff['entity_mentioned'] == selected_console]
    if selected_company != 'All': dff = dff[dff['entity_mentioned'] == selected_company]

    total_mentions = len(dff)
    if total_mentions > 0:
        positive_pct = f"{100 * (dff['sentiment_label'] == 'positive').sum() / total_mentions:.1f}%"
        top_entity = dff['entity_mentioned'].mode()[0]
        sentiment_counts = dff['sentiment_label'].value_counts()
        overall_sentiment = sentiment_counts.idxmax().capitalize()
    else:
        positive_pct, top_entity, overall_sentiment = "0%", "N/A", "N/A"

    dff['date'] = pd.to_datetime(dff['timestamp']).dt.date
    sentiment_over_time = dff.groupby(['date', 'sentiment_label']).size().reset_index(name='count')
    
    fig_history = px.line(
        sentiment_over_time, x='date', y='count', color='sentiment_label',
        title='Historial de Sentimiento Diario', labels={'date': 'Fecha', 'count': 'Número de Menciones', 'sentiment_label': 'Sentimiento'},
        template='plotly_dark', color_discrete_map=SENTIMENT_COLORS, markers=True
    )
    fig_history.update_layout(paper_bgcolor='black', plot_bgcolor='black')

    sentiment_dist = dff['sentiment_label'].value_counts()
    fig_pie = px.pie(values=sentiment_dist.values, names=sentiment_dist.index, title='Distribución de Sentimiento', template='plotly_dark', color=sentiment_dist.index, color_discrete_map=SENTIMENT_COLORS, hole=.4)
    fig_pie.update_traces(textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, paper_bgcolor='black', plot_bgcolor='black')

    top_entities = top_entities_df['entity_mentioned'].value_counts().nlargest(10).sort_values(ascending=True)
    fig_top_entities = px.bar(x=top_entities.values, y=top_entities.index, orientation='h', title='Top 10 Entidades más Mencionadas (General)', labels={'x': 'Número de Menciones', 'y': 'Entidad'}, template='plotly_dark', text=top_entities.values)
    fig_top_entities.update_traces(marker_color='#0d6efd', textposition='outside')
    fig_top_entities.update_layout(paper_bgcolor='black', plot_bgcolor='black')

    return str(total_mentions), positive_pct, top_entity, overall_sentiment, fig_history, fig_pie, fig_top_entities

# --- RUN APP ---
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)