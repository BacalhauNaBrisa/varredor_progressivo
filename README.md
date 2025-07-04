# 🎸 Varredor Progressivo

![Logótipo](https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png)

Explore todos os artistas e álbuns de rock progressivo catalogados no site ProgArchives de forma interativa!

## 🌐 Funcionalidades

- 📌 **Mapa Mundial Interativo**: clique ou selecione um país para filtrar os artistas por origem
- 📋 **Tabela com Filtros**: veja todos os dados (artista, estilo, país, álbum, ano, avaliação)
- ⭐ **Weighted Rating**: cálculo de avaliação ponderada com fórmula bayesiana
- 🔍 Ordenação e filtragem de dados em tempo real

## 🧮 Weighted Rating

A pontuação ponderada é calculada usando a seguinte fórmula bayesiana:

Weighted Rating = ((v / (v + m)) * R) + ((m / (v + m)) * C)


Onde:

- **R** = avaliação média do álbum  
- **v** = número de avaliações do álbum  
- **m** = número mínimo de avaliações requerido (percentil 75%)  
- **C** = avaliação média de todos os álbuns com pelo menos 1 avaliação  

Álbuns com 0 avaliações têm Weighted Rating = 0.

## 📊 Fonte dos Dados

O arquivo CSV contém os seguintes campos:

- `artist_name`  
- `style`  
- `country`  
- `album_name`  
- `year`  
- `rating`  
- `num_ratings`

## 🚀 Acesse o App Online

👉 [Clique aqui para acessar o app no Streamlit Cloud](https://progarchives-streamlit.streamlit.app/)

## 💻 Rodando Localmente

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/BacalhauNaBrisa/progarchives-streamlit.git
cd progarchives-streamlit
pip install -r requirements.txt
streamlit run app.py
