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
    page_title = "Visão Cidades", 
    layout="wide",
    page_icon="🏙"
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

def get_fig1(df):
    df_aux1 = df.loc[:, ["city", "restaurant_id", "country_code"]].groupby(["city", "country_code"]).nunique().reset_index()
    df_aux2 = df_aux1.head(10)
    fig = px.bar(df_aux2, 
                x="city", 
                y ="restaurant_id", 
                color="country_code", 
                labels={"restaurant_id": "Número de restaurantes", "city" : "Cidades", "country_code":"País"})

    return fig

def get_fig2(df):
    linhas_selecionadas = df["aggregate_rating"] > 4
    df_aux = df.loc[linhas_selecionadas, ["city", "aggregate_rating", "country_code"]].groupby(["city", "country_code"]).mean().reset_index()
    df_aux = df_aux.sort_values(by = "aggregate_rating", ascending=False).reset_index(drop=True)
    df_aux1 = df_aux.head(5)
    fig = px.bar(df_aux1, 
                x="city", 
                y ="aggregate_rating", 
                color="country_code", 
                labels={"aggregate_rating": "Nota avaliação média", "city" : "Cidades", "country_code": "País"})
    return fig 

def get_fig3(df):
    df_aux = df.loc[:, ["price_range", "country_code", "city"]].groupby(["city","country_code"]).mean().reset_index()
    df_aux = df_aux.sort_values(by="price_range", ascending=False).reset_index(drop=True)
    df_aux = df_aux.head(10)
    fig = px.bar(df_aux, 
        x="city", 
        y ="price_range", 
        color="country_code", 
        labels={"price_range": "Nota de Preço (até 4)", "city" : "Cidades", "country_code": "País"})
    return fig 

def df_aggregate_rating_zero(df):
    linhas_selecionadas = df["aggregate_rating"] < 2.5
    linhas_selecionadas = (df["aggregate_rating"] == 0)
    df_aux = df.loc[linhas_selecionadas, ["city", "aggregate_rating"]].groupby(["city"]).count().reset_index()
    df_aux = df_aux.sort_values(by = "aggregate_rating", ascending=False).reset_index(drop=True)
    df_aux = df_aux.rename(columns={"city": "Cidade", "aggregate_rating": "Quantidade de notas zero"})

    return df_aux

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
st.header("Visão Cidades")

with st.container():
    st.markdown("##### Top 10 cidades com mais restaurantes na Base de Dados")
    
    fig1 = get_fig1(df)

    st.plotly_chart(fig1, use_container_width=True)

with st.container():
        st.markdown("##### Top 5 cidades com Restaurantes de melhor avaliação média ")
        fig2 = get_fig2(df)
        st.plotly_chart(fig2)
            
    
        
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Top 10 cidades avaliações de preços mais caros")
        fig3 = get_fig3(df)
        st.plotly_chart(fig3, use_container_width=True)
            
        

    with col2:
        st.markdown("##### Cidades que com mais avaliações iguais a zero: ")
        df_aux = df_aggregate_rating_zero(df)
        st.dataframe(df_aux)
# with st.container():
#     st.markdown("Top 10 cidades com mais restaurantes com tipos culinários distintos")
#         #