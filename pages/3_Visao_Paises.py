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
    page_title = "Visão Países", 
    layout="wide",
    page_icon="🌎"
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

def get_fig4(df):
    df_aux = df.loc[:, ["country_code", "restaurant_id"]].groupby(["country_code"]).nunique().reset_index()
    df_aux = df_aux.sort_values(by = "restaurant_id", ascending=False) .reset_index(drop=True)
    df_aux.head(10)
    fig = px.bar(df_aux, 
                        x="country_code", 
                        y ="restaurant_id", 
                        color="restaurant_id", 
                        labels={"country_code": "País", "restaurant_id" : "Quantidade de restaurantes"})

    return fig

def get_fig6(df):
    df_aux = df.loc[:, ["country_code", "city"]].groupby(["country_code"]).nunique().reset_index()
    df_aux = df_aux.head(10)
    df_aux = df_aux.sort_values(by = "city", ascending=False) .reset_index(drop=True)
    fig = px.bar(df_aux, 
                        x="country_code", 
                        y ="city", 
                        color="city", 
                        labels={"city": "Quantidade de Cidades", "country_code": "País"})

    return fig



def get_fig7(df):
    df_aux = df.loc[:, ["aggregate_rating", "country_code"]].groupby("country_code").mean().reset_index()
    df_aux = df_aux.sort_values(by="aggregate_rating", ascending=False)
    fig = px.bar(df_aux, 
                    x="country_code", 
                    y ="aggregate_rating", 
                    color="aggregate_rating", 
                    labels={"aggregate_rating": "Nota média ", "country_code": "País"})
    
    return fig

def get_fig8(df):
    df_aux = df.loc[(df["average_cost_for_two_dolar"] < 1000000),:]
    df_aux = df_aux.loc[:, ["country_code", "average_cost_for_two_dolar"]].groupby(["country_code"]).mean().reset_index()
    df_aux = df_aux.sort_values(by="average_cost_for_two_dolar", ascending=False)      
    fig = px.bar(df_aux, 
                            x="country_code", 
                            y ="average_cost_for_two_dolar", 
                            color="average_cost_for_two_dolar", 
                            labels={"average_cost_for_two_dolar": "Valor (dolar) ", "country_code": "País"})

#===============================================================================

df_raw = pd.read_csv("pages/utils/zomato.csv")
df = df_raw.copy()
df = rename_columns(df)
df = clean_data(df)

### Limpeza dos dados


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
st.header("Visão Paises")

with st.container():
    st.markdown("##### Top 10 países com mais restaurantes registrados")
    fig4 = get_fig4(df)
    st.plotly_chart(fig4)

with st.container():
    st.markdown("##### Top 10 Países com mais Cidades Registradas por País")
    fig6 = get_fig6(df)
    st.plotly_chart(fig6)
    

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Nota Média de Avaliações Feita")
        st.markdown("##### por País")
        fig = get_fig7(df)
        st.plotly_chart(fig)

    with col2:
        st.markdown("##### Preço Médio de um Prato para 2 Pessoas")
        st.markdown("##### por País")
        fig8 = get_fig8(df)
        st.plotly_chart(fig)
                