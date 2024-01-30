import pandas as pd
import sys
import numpy
import inflection
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go 
from haversine import haversine
from datetime import datetime
from PIL import Image
import folium
import streamlit_folium
#from pages.utils.util import *
# Limpeza dos dados
# Funções:


def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
    
    
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

df_raw = pd.read_csv("zomato.csv")
df = df_raw.copy()
### Limpeza dos dados

df = rename_columns(df)
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}


# Mudança de coluna
df['country_code'] = df['country_code'].map(COUNTRIES)

# Criação de uma nova coluna cost range
df["cost_range"] = df.loc[:, "price_range"].apply(lambda x : create_price_tye(x))
df["cuisines"] = df["cuisines"].astype(str)
df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
# PRECISO TRANSFORMAR TUDO EM DOLAR
# Transformar os obejtos em strings. Exemplo: A coluna cuisines

df = df.astype({"restaurant_id": int})

#===================
# Barra Lateal
#===================

image = Image.open("image.webp")

st.sidebar.image(image, width=200)
st.sidebar.markdown("# Zomato Case Study")
st.sidebar.markdown("""---""")
st.sidebar.markdown("## Selecione um país")

# Filtro de País

country_select = st.sidebar.multiselect(
    "",
    (df["country_code"].unique()),
    default = (df["country_code"].unique())
)

# Filtro por preço:
cost_select = st.sidebar.multiselect(
    "Selecione a classificação de preço: ",
    (df["cost_range"].unique()),
    default = (df["cost_range"].unique())
)
# Aplicando os filtros
linhas_selecionadas = df["country_code"].isin(country_select)
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df["cost_range"].isin(cost_select)
df = df.loc[linhas_selecionadas, :]
# Dale!

# ============================================================================
# Layout do Streamlit
# ============================================================================

st.header("Visão Geral")
st.markdown("Onde  estamos:")

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("##### Restaurantes cadastrados")
        # INFO:
    with col2:
        st.markdown("##### Paises cadastrados")
        # INFO 
    with col3:
        st.markdown("##### Avaliações feitas na plataforma")
        #INFO 
    with col4:
        st.markdown("##### Cidades cadastradas")
        #INFO

with st.container():
    # MAPA AQUI
    pass



