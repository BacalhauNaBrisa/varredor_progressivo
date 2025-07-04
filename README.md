# ![Logótipo](https://github.com/BacalhauNaBrisa/varredor_progressivo/raw/main/assets/logo.png)

# Varredor Progressivo 🎸🌍

Aplicação em [Streamlit Cloud](https://varredorprogressivo.streamlit.app) que explora a base de dados de álbuns de rock progressivo retirados do site [ProgArchives.com](https://www.progarchives.com).

---

## ⚙️ Funcionalidades

- Carregamento automático do CSV hospedado no GitHub
- Visualização interativa dos dados em tabela
- Mapa mundial com contagem de álbuns por país
- Filtros por país, estilo e ano (multiseleção)
- Cálculo de "Weighted Rating" com média bayesiana
- Ranking dos 10 melhores álbuns por país e estilo
- Exportação dos dados filtrados para CSV
- Tema claro e escuro com modo mobile otimizado
- Exibe a data da última atualização do CSV (via GitHub API)

---

## 📦 Instalação Local

1. Clone o repositório:

```bash
git clone https://github.com/BacalhauNaBrisa/varredor_progressivo.git
cd varredor_progressivo
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie o arquivo .streamlit/secrets.toml com seu token do GitHub:

```bash
GITHUB_TOKEN = "ghp_seu_token_aqui"
```

5. Execute a aplicação:

```bash
streamlit run app.py
```

🚀 Deploy no Streamlit Cloud

1. Suba este projeto para um repositório GitHub (já está pronto para isso)

2. Vá até Streamlit Cloud

3. Crie um novo app, selecione este repositório e o arquivo app.py

4. Vá em Settings > Secrets e adicione:

```bash
GITHUB_TOKEN = "ghp_seu_token_aqui"
```

5. Clique em "Deploy"

📁 Estrutura do Projeto

varredor_progressivo/
├── app.py
├── requirements.txt
├── progarchives_all_artists_albums.csv
├── assets/
│   └── logo.png
└── .streamlit/
    └── config.toml

🧮 Fórmula do Weighted Rating

A nota ponderada é calculada com base na média bayesiana:

```bash
Weighted Rating = ((v / (v + m)) * R) + ((m / (v + m)) * C)
```

Onde:

    R = nota média do álbum

    v = número de avaliações do álbum

    m = percentil 75 da distribuição de número de avaliações (limite mínimo para confiabilidade)

    C = média global das notas de todos os álbuns com pelo menos 1 avaliação

📅 Última atualização automática

A data da última atualização do CSV é buscada diretamente via GitHub API e exibida no topo da aplicação. Caso falhe, exibe "Last updated on July 04, 2025"

📜 Licença

MIT — sinta-se livre para usar, modificar e contribuir!
