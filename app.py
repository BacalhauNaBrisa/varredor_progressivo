import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
from datetime import datetime

# Constants
CSV_URL = "https://raw.githubusercontent.com/BacalhauNaBrisa/varredor_progressivo/main/progarchives_all_artists_albums.csv"
LOGO_URL = "https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png"

# Page config
st.set_page_config(page_title="Varredor Progressivo", layout="centered")

# Get last updated date of CSV from GitHub API
@st.cache_data(ttl=3600)
def get_last_modified_date_from_github():
    api_url = "https://api.github.com/repos/BacalhauNaBrisa/varredor_progressivo/commits"
    params = {"path": "progarchives_all_artists_albums.csv", "per_page": 1}
    headers = {"Accept": "application/vnd.github+json"}
    try:
        resp = requests.get(api_url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            st.error(f"GitHub API error: {resp.status_code}")
            return "Last updated: unknown"
        data = resp.json()
        if not isinstance(data, list) or not data:
            st.error("No commit data found for CSV file.")
            return "Last updated: unknown"
        dt_str = data[0]["commit"]["committer"]["date"]
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("Last updated on %B %d, %Y")
    except Exception as e:
        st.error(f"Error fetching GitHub date: {e}")
        return "Last updated: unknown"

# Load and cache data
@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_csv(CSV_URL)
    df['num_ratings'] = pd.to_numeric(df['num_ratings'], errors='coerce').fillna(0).astype(int)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
    return df

def compute_weighted_rating(df):
    valid_ratings = df[df['num_ratings'] > 0]
    if valid_ratings.empty:
        C, m = 0, 0
    else:
        C = valid_ratings['rating'].mean()
        m = valid_ratings['num_ratings'].quantile(0.75)

    def bayesian(row):
        v = row['num_ratings']
        R = row['rating']
        if v == 0 or pd.isna(R) or pd.isna(v):
            return 0
        return ((v / (v + m)) * R) + ((m / (v + m)) * C)

    df['Weighted Rating'] = df.apply(bayesian, axis=1)
    return df

def get_country_map(df):
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    fig = px.choropleth(
        country_counts,
        locations='country',
        locationmode='country names',
        color='count',
        color_continuous_scale='Viridis',
        title='🌍 Número de Álbuns por País',
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    return fig

# Load data
data = load_data()
data = compute_weighted_rating(data)

# Theme toggle logic
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Apply theme CSS
if st.session_state.theme == "dark":
    st.markdown("""
        <style>
        .main { background-color: #121212; color: #e0e0e0; }
        .sidebar .sidebar-content { background-color: #1f1f1f; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .main { background-color: white; color: black; }
        .sidebar .sidebar-content { background-color: #f0f2f6; }
        </style>
    """, unsafe_allow_html=True)

# Sidebar UI
st.sidebar.image(LOGO_URL, width=150)
st.sidebar.markdown(f"🗓️ {get_last_modified_date_from_github()}")
st.sidebar.title("🎸 Varredor Progressivo")
st.sidebar.markdown("Explore artistas e álbuns de rock progressivo")

# Theme toggle
st.sidebar.markdown("---")
st.sidebar.write("**Tema:**")
st.sidebar.button(
    f"Trocar para {'Dark' if st.session_state.theme == 'light' else 'Light'} Mode",
    on_click=toggle_theme
)

# Initialize filter state
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "Todos"
if "selected_styles" not in st.session_state:
    st.session_state.selected_styles = []
if "selected_years" not in st.session_state:
    st.session_state.selected_years = []

def reset_filters():
    st.session_state.selected_country = "Todos"
    st.session_state.selected_styles = []
    st.session_state.selected_years = []

# Sidebar filters
st.sidebar.markdown("### 🎛️ Filtros")

country_options = ["Todos"] + sorted(data['country'].dropna().unique().tolist())
style_options = sorted(data['style'].dropna().unique().tolist())
year_options = sorted(data['year'].dropna().unique().astype(int))

st.sidebar.selectbox(
    "Filtrar por País",
    country_options,
    index=country_options.index(st.session_state.selected_country),
    key="selected_country"
)

st.sidebar.multiselect(
    "Filtrar por Estilo(s)",
    style_options,
    default=st.session_state.selected_styles,
    key="selected_styles"
)

st.sidebar.multiselect(
    "Filtrar por Ano(s)",
    year_options,
    default=st.session_state.selected_years,
    key="selected_years"
)

st.sidebar.button("🔄 Resetar Filtros", on_click=reset_filters)

# Display country map
st.subheader("🌍 Mapa Interativo por País")
st.plotly_chart(get_country_map(data), use_container_width=True)

# Filter data
filtered_data = data.copy()
if st.session_state.selected_country != "Todos":
    filtered_data = filtered_data[filtered_data['country'] == st.session_state.selected_country]
if st.session_state.selected_styles:
    filtered_data = filtered_data[filtered_data['style'].isin(st.session_state.selected_styles)]
if st.session_state.selected_years:
    filtered_data = filtered_data[filtered_data['year'].isin(st.session_state.selected_years)]

# Show filtered table
st.subheader("📊 Tabela de Álbuns Filtrados")
st.dataframe(filtered_data.sort_values(by='Weighted Rating', ascending=False), use_container_width=True)

# Export filtered data
st.download_button(
    label="📥 Exportar CSV Filtrado",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='varredor_progressivo_filtrado.csv',
    mime='text/csv'
)

# Aggregated statistics
st.subheader("📈 Estatísticas Agrupadas")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Média de Avaliação por Estilo")
    avg_rating_by_style = (
        filtered_data
        .groupby('style')['rating']
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.dataframe(avg_rating_by_style, use_container_width=True)

with col2:
    st.markdown("#### Média de Weighted Rating por País")
    avg_weighted_by_country = (
        filtered_data
        .groupby('country')['Weighted Rating']
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.dataframe(avg_weighted_by_country, use_container_width=True)

# Top 10 albums
st.subheader("🏆 Top 10 Álbuns")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Por Estilo")
    for style in st.session_state.selected_styles[:1]:
        st.markdown(f"**Estilo:** {style}")
        top_by_style = (
            filtered_data[filtered_data['style'] == style]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(top_by_style[['artist_name', 'album_name', 'year', 'Weighted Rating']], use_container_width=True)

with col2:
    st.markdown("#### Por País")
    if st.session_state.selected_country != "Todos":
        st.markdown(f"**País:** {st.session_state.selected_country}")
        top_by_country = (
            filtered_data[filtered_data['country'] == st.session_state.selected_country]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(top_by_country[['artist_name', 'album_name', 'year', 'Weighted Rating']], use_container_width=True)
