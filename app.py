import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Constants
CSV_URL = "https://raw.githubusercontent.com/BacalhauNaBrisa/progarchives-streamlit/main/progarchives_all_artists_albums.csv"
LOGO_URL = "https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png"

# Config
st.set_page_config(page_title="Varredor Progressivo", layout="wide")

# Show logo and title
st.image(LOGO_URL, width=200)
st.title("🎸 Varredor Progressivo")
st.markdown("Explore artistas e álbuns de rock progressivo de forma interativa com filtros, mapa mundial e avaliações ponderadas!")

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df['num_ratings'] = pd.to_numeric(df['num_ratings'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    return df

def compute_weighted_rating(df):
    valid_ratings = df[df['num_ratings'] > 0]
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

    fig.update_layout(clickmode='event+select')
    return fig

# Load and process data
data = load_data()
data = compute_weighted_rating(data)

# Mapa
st.subheader("🌍 Mapa Interativo por País")
map_fig = get_country_map(data)
map_click = st.plotly_chart(map_fig, use_container_width=True)

# Filtros
st.subheader("🎛️ Filtros")
with st.expander("Mostrar/Ocultar Filtros"):
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_country = st.selectbox("Filtrar por País", ["Todos"] + sorted(data['country'].dropna().unique().tolist()))

    with col2:
        selected_styles = st.multiselect("Filtrar por Estilo(s)", sorted(data['style'].dropna().unique().tolist()), default=[])

    with col3:
        available_years = sorted(data['year'].dropna().unique().astype(int))
        selected_years = st.multiselect("Filtrar por Ano(s)", available_years, default=[])

    reset_filters = st.button("🔄 Resetar Filtros")

# Map click
clicked_country = None
if map_click and map_click.selection and 'points' in map_click.selection:
    points = map_click.selection['points']
    if points:
        clicked_country = points[0].get('location')

# Reset
if reset_filters:
    selected_country = "Todos"
    selected_styles = []
    selected_years = []
    clicked_country = None
    st.experimental_rerun()

# Filtered data
filtered_data = data.copy()

if clicked_country:
    filtered_data = filtered_data[filtered_data['country'] == clicked_country]
    st.info(f"País selecionado no mapa: **{clicked_country}**")
elif selected_country != "Todos":
    filtered_data = filtered_data[filtered_data['country'] == selected_country]

if selected_styles:
    filtered_data = filtered_data[filtered_data['style'].isin(selected_styles)]

if selected_years:
    filtered_data = filtered_data[filtered_data['year'].isin(selected_years)]

# Tabela de dados
st.subheader("📊 Tabela de Álbuns Filtrados")

st.dataframe(
    filtered_data.sort_values(by='Weighted Rating', ascending=False),
    use_container_width=True
)

# Export CSV
st.download_button(
    label="📥 Exportar CSV Filtrado",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='varredor_progressivo_filtrado.csv',
    mime='text/csv'
)

# Estatísticas agrupadas
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

# Top 10 Álbuns
st.subheader("🏆 Top 10 Álbuns")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Por Estilo")
    for style in selected_styles[:1]:  # Show top 10 for the first selected style
        st.markdown(f"**Estilo:** {style}")
        top_by_style = (
            filtered_data[filtered_data['style'] == style]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(top_by_style[['artist_name', 'album_name', 'year', 'Weighted Rating']], use_container_width=True)

with col2:
    st.markdown("#### Por País")
    country_to_show = clicked_country if clicked_country else (selected_country if selected_country != "Todos" else None)
    if country_to_show:
        st.markdown(f"**País:** {country_to_show}")
        top_by_country = (
            filtered_data[filtered_data['country'] == country_to_show]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(top_by_country[['artist_name', 'album_name', 'year', 'Weighted Rating']], use_container_width=True)
