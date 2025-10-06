import sys
sys.path.append('config')
import config
from src.datamanager import DataManager
import streamlit as st
import plotly.express as px

#streamlit run app.py

#Initialisation du gestionnaire de données
dm = DataManager()

# Récupération des données
df_sexe = dm.getSexeRepartition()

# Affichage du titre
st.title("Répartition par sexe")

# Création du camembert avec Plotly
fig = px.pie(df_sexe, 
             values='nb', 
             names='sexe',
             title='Répartition par sexe des conseillers')


# Affichage du graphique
st.plotly_chart(fig)

# Récupération des données
df_age = dm.getAgeRepartition()
fig = px.bar(
    x=[str(label) for label in df_age["labels"]], 
    y=df_age['values'],
    labels={'x': 'Tranche d\'âge', 'y': 'Nombre de personnes'},
    title='Répartition par tranches d\'âge'
)
fig.update_xaxes(type='category')

st.plotly_chart(fig)


#todo :
#Ratio H/F (cameberr)
#Répartition par tranche d'âge
