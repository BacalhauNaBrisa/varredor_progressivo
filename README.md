# ![Logótipo](https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png)

# Varredor Progressivo

Um aplicativo web feito com **Streamlit** para explorar artistas e álbuns de rock progressivo usando dados do ProgArchives.

---

## Funcionalidades

- Carrega automaticamente o arquivo CSV com mais de 48 mil registros hospedado no GitHub.
- Tabela interativa com filtros por:
  - País
  - Estilo musical (multiseleção)
  - Ano(s) (multiseleção)
- Cálculo do **Weighted Rating** (Avaliação Ponderada) usando média bayesiana para dar maior peso a avaliações confiáveis.
- Mapa mundial interativo mostrando número de álbuns por país.
- Exportação dos dados filtrados em CSV.
- Estatísticas agregadas por país e por estilo.
- Top 10 álbuns por país ou estilo.
- Tema claro/escuro com toggle no sidebar.
- Layout otimizado para desktop e dispositivos móveis.

---

## Como usar

1. Clone este repositório:

```bash
git clone https://github.com/BacalhauNaBrisa/varredor_progressivo.git
cd varredor_progressivo

Instale as dependências:

pip install -r requirements.txt

Execute localmente:

streamlit run app.py

Para hospedar no Streamlit Cloud:

Faça o push do repositório no GitHub (já configurado com .streamlit/config.toml para tema padrão)

Crie um novo app no Streamlit Cloud apontando para seu repositório

O app será automaticamente executado e acessível via URL pública

Arquivos principais

    app.py — código do aplicativo Streamlit

    requirements.txt — bibliotecas Python necessárias

    .streamlit/config.toml — configuração do tema padrão (claro ou escuro)

    progarchives_all_artists_albums.csv — CSV hospedado no GitHub (não incluído no repositório local, carregado remotamente)

Bibliotecas utilizadas

    streamlit

    pandas

    plotly
