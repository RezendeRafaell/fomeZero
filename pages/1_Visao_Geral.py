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
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title = "Visão Geral", 
    layout="wide",
    page_icon="📈"
)

#=================================
# Dicionários
#=================================

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

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}


CURRENCIES = {
"Botswana Pula(P)": 0.074,
"Brazilian Real(R$)": 0.20,
"Dollar($)": 1,
"Emirati Diram(AED)": 0.27,
"Indian Rupees(Rs.)": 0.012,
"Indonesian Rupiah(IDR)": 0.000063,
"NewZealand($)": 0.61,
"Pounds(£)": 1.27,
"Qatari Rial(QR)": 0.27,
"Rand(R)": 0.054,
"Sri Lankan Rupee(LKR)": 0.0032,
"Turkish Lira(TL)": 0.033
}

#===========================
# FUNÇÕES
#===========================

def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

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



def clean_data(df):
    # Mudança de coluna
    # Criação de uma nova coluna cost range
    df['country_code'] = df['country_code'].map(COUNTRIES)
    df["cost_range"] = df.loc[:, "price_range"].apply(lambda x : create_price_tye(x))
    df["cuisines"] = df["cuisines"].astype(str)
    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

    df['exchange_to_dolar'] = df['currency'].map(CURRENCIES)

    df['average_cost_for_two_dolar'] = df['average_cost_for_two'] * df['exchange_to_dolar']


    df = df.loc[(df["average_cost_for_two_dolar"] < 1000000), :].copy()
    df = df.astype({"restaurant_id": int})

    return df

def map_maker(df):
    df_aux = (df.loc[:, ["restaurant_name","average_cost_for_two_dolar","cuisines", "aggregate_rating" ,"latitude", "longitude"]])

    mapa = folium.Map()

    marker = MarkerCluster().add_to(mapa)

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info["latitude"],
                    location_info["longitude"]],
                    popup = f"""
                            <strong>{location_info['restaurant_name']}</strong> 
                            Preço médio para dois($): {location_info['average_cost_for_two_dolar']}\n 
                            Tipo: {location_info['cuisines']}\n
                            Nota: {location_info['aggregate_rating']}\n
                        """,
                    icon=folium.Icon(color = 'green')).add_to(marker)

    streamlit_folium.folium_static(mapa, width=1024, height=600)


#===============================================================================

df_raw = pd.read_csv("data_set/zomato.csv")
df = df_raw.copy()
df = rename_columns(df)
df = clean_data(df)

### Limpeza dos dados


#===================
# Barra Lateal
#===================

image = Image.open("image.webp")

st.sidebar.image(image, width=200)
st.sidebar.markdown("# Zomato's Geographic Analysis")
st.sidebar.markdown("""---""")
st.sidebar.markdown("## Selecione um país")

# Filtro de País

country_select = st.sidebar.multiselect(
    "",
    (df["country_code"].unique()),
    default=(df["country_code"].unique())
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

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Rezende Rafael")

#========================================================================================

# ============================================================================
# Layout do Streamlit
# ============================================================================

st.header("Visão Geral")


with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("##### Restaurantes cadastrados")
        st.markdown(f"## {(df.loc[:, 'restaurant_id'].nunique())}")
    with col2:    
        st.markdown("##### Paises cadastrados")
        st.markdown("")
        st.markdown(f"## {df.loc[:, 'country_code'].nunique() }")

    with col3:
        st.markdown("##### Avaliações feitas na plataforma")
        st.markdown(f"## {df.loc[:, 'votes'].sum()}")


    with col4:
        st.markdown("##### Cidades cadastradas")
        st.markdown(f"## {df.loc[:, 'city'].nunique()}")

with st.container():
    
    st.markdown("## Nossos Restaurantes")
    map_maker(df)



