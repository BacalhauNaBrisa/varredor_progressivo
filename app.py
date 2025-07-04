import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Constants
CSV_URL = "https://raw.githubusercontent.com/BacalhauNaBrisa/varredor_progressivo/main/progarchives_all_artists_albums.csv"
LOGO_URL = "https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png"

# Page config with centered layout to look good on desktop and mobile
st.set_page_config(page_title="Varredor Progressivo", layout="wide")

# Load and cache data once
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
        C = 0
        m = 0
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

# Theme toggle logic with session state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Apply basic theme styles with CSS injection
if st.session_state.theme == "dark":
    st.markdown(
        """
        <style>
        .main {
            background-color: #121212;
            color: #e0e0e0;
        }
        .sidebar .sidebar-content {
            background-color: #1f1f1f;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .main {
            background-color: white;
            color: black;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Show logo and title
st.sidebar.image(LOGO_URL, width=150)
st.sidebar.title("🎸 Varredor Progressivo")
st.sidebar.markdown("Explore artistas e álbuns de rock progressivo")

# Theme toggle button in sidebar
st.sidebar.markdown("---")
st.sidebar.write("**Tema:**")
st.sidebar.button(f"Trocar para {'Dark' if st.session_state.theme=='light' else 'Light'} Mode", on_click=toggle_theme)

# Initialize filters in session state if not present
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "Todos"
if "selected_styles" not in st.session_state:
    st.session_state.selected_styles = []
if "selected_years" not in st.session_state:
    st.session_state.selected_years = []

# Sidebar filters
st.sidebar.markdown("### 🎛️ Filtros")

country_options = ["Todos"] + sorted(data['country'].dropna().unique().tolist())
style_options = sorted(data['style'].dropna().unique().tolist())
year_options = sorted(data['year'].dropna().unique().astype(int))

selected_country = st.sidebar.selectbox(
    "Filtrar por País", country_options, index=country_options.index(st.session_state.selected_country), key="selected_country"
)
selected_styles = st.sidebar.multiselect(
    "Filtrar por Estilo(s)", style_options, default=st.session_state.selected_styles, key="selected_styles"
)
selected_years = st.sidebar.multiselect(
    "Filtrar por Ano(s)", year_options, default=st.session_state.selected_years, key="selected_years"
)

if st.sidebar.button("🔄 Resetar Filtros"):
    st.session_state.selected_country = "Todos"
    st.session_state.selected_styles = []
    st.session_state.selected_years = []
    st.experimental_rerun()

# Show main map
st.subheader("🌍 Mapa Interativo por País")
map_fig = get_country_map(data)
st.plotly_chart(map_fig, use_container_width=True)

# Apply filters
filtered_data = data.copy()
if selected_country != "Todos":
    filtered_data = filtered_data[filtered_data['country'] == selected_country]
if selected_styles:
    filtered_data = filtered_data[filtered_data['style'].isin(selected_styles)]
if selected_years:
    filtered_data = filtered_data[filtered_data['year'].isin(selected_years)]

# Show filtered table
st.subheader("📊 Tabela de Álbuns Filtrados")
st.dataframe(filtered_data.sort_values(by='Weighted Rating', ascending=False), use_container_width=True)

# Export CSV button
st.download_button(
    label="📥 Exportar CSV Filtrado",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='varredor_progressivo_filtrado.csv',
    mime='text/csv'
)

# Show aggregated stats
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

# Top 10 Albums
st.subheader("🏆 Top 10 Álbuns")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Por Estilo")
    for style in selected_styles[:1]:
        st.markdown(f"**Estilo:** {style}")
        top_by_style = (
            filtered_data[filtered_data['style'] == style]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(top_by_style[['artist_name', 'album_name', 'year', 'Weighted Rating']], use_container_width=True)

with col2:
    st.markdown("#### Por País")
    if selected_country != "Todos":
        st.markdown(f"**País:** {selected_country}")
        top_by_country = (
            filtered_data[filtered_data['country'] == selected_country]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(top_by_country[['artist_name', 'album_name', 'year', 'Weighted Rating']], use_container_width=True)
