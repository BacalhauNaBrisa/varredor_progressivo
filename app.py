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
st.set_page_config(
    page_title="Varredor Progressivo",
    page_icon="https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.ico",
    layout="centered"
)

# Get last updated date of CSV from GitHub API with fallback
@st.cache_data(ttl=3600)
def get_last_modified_date_from_github():
    api_url = "https://api.github.com/repos/BacalhauNaBrisa/varredor_progressivo/commits"
    params = {"path": "progarchives_all_artists_albums.csv", "per_page": 1}
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {st.secrets.get('GITHUB_TOKEN', '')}"
    }
    try:
        resp = requests.get(api_url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return "Last updated on July 4, 2025"
        data = resp.json()
        if not isinstance(data, list) or not data:
            return "Last updated on July 4, 2025"
        dt_str = data[0]["commit"]["committer"]["date"]
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("Last updated on %B %d, %Y")
    except Exception:
        return "Last updated on July 4, 2025"

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
        title='🌍 Number of Albums per Country',
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
st.sidebar.title("Varredor Progressivo")
st.sidebar.markdown("Explore progressive rock artists and albums")

# Theme toggle
st.sidebar.markdown("---")
st.sidebar.write("**Theme:**")
st.sidebar.button(
    f"Switch to {'Dark' if st.session_state.theme == 'light' else 'Light'} Mode",
    on_click=toggle_theme
)

# Initialize filter state
if "selected_countries" not in st.session_state:
    st.session_state.selected_countries = ["All"]
if "selected_styles" not in st.session_state:
    st.session_state.selected_styles = []
if "selected_years" not in st.session_state:
    st.session_state.selected_years = []

def reset_filters():
    st.session_state.selected_countries = ["All"]
    st.session_state.selected_styles = []
    st.session_state.selected_years = []

# Sidebar filters
st.sidebar.markdown("### 🎛️ Filters")

country_options = ["All"] + sorted(data['country'].dropna().unique().tolist())
style_options = sorted(data['style'].dropna().unique().tolist())
year_options = sorted(data['year'].dropna().unique().astype(int))

st.sidebar.multiselect(
    "Filter by Country",
    country_options,
    key="selected_countries"
)

st.sidebar.multiselect(
    "Filter by Style(s)",
    style_options,
    key="selected_styles"
)

st.sidebar.multiselect(
    "Filter by Year(s)",
    year_options,
    key="selected_years"
)

st.sidebar.button("🔄 Reset Filters", on_click=reset_filters)

# Display Logo in st.markdown() Header on the Homepage
st.markdown(
    f"<div style='text-align: center;'>"
    f"<img src='{LOGO_URL}' width='150'><br>"
    f"<h2 style='margin-top: 0;'>Varredor Progressivo</h2>"
    f"</div>",
    unsafe_allow_html=True
)

# Display country map
st.subheader("🌍 Interactive Map by Country")
st.plotly_chart(get_country_map(data), use_container_width=True)

# Filter data
filtered_data = data.copy()
selected_countries = st.session_state.selected_countries

if "All" not in selected_countries:
    filtered_data = filtered_data[filtered_data['country'].isin(selected_countries)]
if st.session_state.selected_styles:
    filtered_data = filtered_data[filtered_data['style'].isin(st.session_state.selected_styles)]
if st.session_state.selected_years:
    filtered_data = filtered_data[filtered_data['year'].isin(st.session_state.selected_years)]

# Show filtered table
st.subheader("📊 Filtered Albums Table")
st.dataframe(
    filtered_data.sort_values(by='Weighted Rating', ascending=False)
    .reset_index(drop=True)
    .set_index(pd.Index(range(1, len(filtered_data) + 1))),
    use_container_width=True
)

# Export filtered data
st.download_button(
    label="📥 Export Filtered CSV",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='varredor_progressivo_filtered.csv',
    mime='text/csv'
)

# Top 10 albums
st.subheader("🏆 Top 10 Albums")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### By Style")
    for style in st.session_state.selected_styles[:1]:
        st.markdown(f"**Style:** {style}")
        top_by_style = (
            filtered_data[filtered_data['style'] == style]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(
            top_by_style[['artist_name', 'album_name', 'year', 'Weighted Rating']]
            .reset_index(drop=True)
            .set_index(pd.Index(range(1, len(top_by_style) + 1))),
            use_container_width=True
        )

with col2:
    st.markdown("#### By Country")
    countries_to_show = [
        c for c in st.session_state.selected_countries if c != "All"
    ][:1]  # show only first for brevity
    for country in countries_to_show:
        st.markdown(f"**Country:** {country}")
        top_by_country = (
            filtered_data[filtered_data['country'] == country]
            .sort_values(by='Weighted Rating', ascending=False)
            .head(10)
        )
        st.dataframe(
            top_by_country[['artist_name', 'album_name', 'year', 'Weighted Rating']]
            .reset_index(drop=True)
            .set_index(pd.Index(range(1, len(top_by_country) + 1))),
            use_container_width=True
        )
