import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Constants
CSV_URL = "https://raw.githubusercontent.com/BacalhauNaBrisa/varredor_progressivo/main/progarchives_all_artists_albums.csv"
LOGO_URL = "https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df['num_ratings'] = pd.to_numeric(df['num_ratings'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    return df

def compute_weighted_rating(df):
    # Filter out albums with 0 ratings
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

def show_world_map(df):
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']

    fig = px.choropleth(
        country_counts,
        locations='country',
        locationmode='country names',
        color='count',
        color_continuous_scale='Viridis',
        title='Number of Albums per Country',
    )

    st.plotly_chart(fig)

    # Let user click on a country from a selectbox to filter
    selected_country = st.selectbox("Filter by Country", ["All"] + sorted(df['country'].dropna().unique().tolist()))
    if selected_country != "All":
        df = df[df['country'] == selected_country]
    return df

# Streamlit App Layout
st.set_page_config(page_title="Varredor Progressivo", layout="wide")
st.image(LOGO_URL, width=200)
st.title("🎸 Varredor Progressivo")
st.markdown("Explore progressive rock albums by artist, country, rating, and more!")

# Load and process data
data = load_data()
data = compute_weighted_rating(data)
filtered_data = show_world_map(data)

# Show interactive table
st.markdown("### 📊 Album Data")
st.dataframe(
    filtered_data.sort_values(by='Weighted Rating', ascending=False),
    use_container_width=True
)
