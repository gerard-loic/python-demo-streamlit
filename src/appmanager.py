from src.datamanager import DataManager
import streamlit as st
from config.config import Config
import numpy as np
import pydeck as pdk
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class AppManager():
    def __init__(self, dm : DataManager):
        self.dm = dm
        self.buildStructure()
        self.buildFilters()
        self.buildGeoStat()
        self.buildSexeStat()
        self.buildAgeStat()
        self.buildCspStat()


    def buildStructure(self):
        st.title(Config.APP_TITLE)
        self.col1, self.col2 = st.columns(2)
        st.set_page_config(layout="wide")

    def buildFilters(self):
        self.filter_departement = st.sidebar.selectbox(
            label="Département", 
            options=self.dm.getDepartements(), 
            on_change=self.onFilterChanged,
            key="departement_select"
            )
        self.filter_fonction = st.sidebar.selectbox(
            label="Fonction", 
            options=self.dm.getFonctions(),
            key="fonction_select"
            )

    def onFilterChanged(self):
        print("FILTER CHANGED !!")
        print(st.session_state.departement_select)

    def buildCspStat(self):
        with self.col2.container(border=True):
            st.subheader("Répartition par CSP")

            data = self.dm.getCspRepartition(st.session_state.departement_select, st.session_state.fonction_select)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=data["labels"],
                x=data["values"] ,  # Valeurs négatives pour afficher à gauche
                name='CSP',
                orientation='h',
                marker=dict(color="#F39E00")
            ))

            fig.update_layout(
                title='Répartition par CSP',
                xaxis=dict(
                    title='Population',
                    tickvals=[0, 500, 1000, 1500, 2000],
                    ticktext=['0', '500', '1000', '1500', '2000']
                ),
                yaxis=dict(title='CSP'),
                barmode='overlay',
                bargap=0.1,
                height=600,
                showlegend=True
            )

            # Afficher le graphique
            st.plotly_chart(fig, use_container_width=True)

    def buildSexeStat(self):
        with self.col2.container(border=True):
            # Affichage du titre
            st.subheader("Répartition par sexe")
            # Création du camembert avec Plotly
            fig = px.pie(self.dm.getSexeRepartition(st.session_state.departement_select, st.session_state.fonction_select), 
                        values='nb', 
                        names='sexe',
                        color_discrete_map={'F': '#FF69B4', 'M': '#4169E1'}
                        )
            
            fig.update_traces(marker=dict(colors=['#FF69B4', '#4169E1']))
            
            st.plotly_chart(fig)

    def buildAgeStat(self):
        with self.col1.container(border=True):
            #Affichage du titre
            st.subheader("Répartition par âge")
            fig = go.Figure()

            dfH = self.dm.getAgeRepartition(st.session_state.departement_select, st.session_state.fonction_select, "M")
            dfHN = np.array(dfH['values']) * -1
            fig.add_trace(go.Bar(
                y=[str(label) for label in dfH["labels"]],
                x=dfHN ,  # Valeurs négatives pour afficher à gauche
                name='Hommes',
                orientation='h',
                marker=dict(color='#4169E1')
            ))

            dfM = self.dm.getAgeRepartition(st.session_state.departement_select, st.session_state.fonction_select, "F")
            fig.add_trace(go.Bar(
                y=[str(label) for label in dfM["labels"]],
                x=dfM['values'],  # Valeurs négatives pour afficher à gauche
                name='Femmes',
                orientation='h',
                marker=dict(color='#FF69B4')
            ))

            # Mise en forme
            fig.update_layout(
                title='Pyramide des âges par sexe',
                xaxis=dict(
                    title='Population',
                    tickvals=[-2000, -1500, -1000, -500, 0, 500, 1000, 1500, 2000],
                    ticktext=['2000', '1500', '1000', '500', '0', '500', '1000', '1500', '2000']
                ),
                yaxis=dict(title='Tranche d\'âge'),
                barmode='overlay',
                bargap=0.1,
                height=600,
                showlegend=True
            )

            # Afficher le graphique
            st.plotly_chart(fig, use_container_width=True)


    def buildGeoStat(self):
        with self.col1.container(border=True):
            st.subheader("Répartition géographique par département")
            chart_data = self.dm.getGeodispersion(st.session_state.departement_select, st.session_state.fonction_select)

            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=46.603354,  # Centre de la France
                    longitude=1.888334,   # Centre de la France
                    zoom=5.5,             # Zoom adapté pour voir toute la France
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        'ColumnLayer',    # Utilisation de ColumnLayer pour des colonnes proportionnelles
                        data=chart_data,
                        get_position='[long, lat]',  # Attention : 'long' dans votre DataFrame
                        get_elevation='nb',           # Hauteur basée sur le nombre de personnes
                        elevation_scale=10,          # Facteur d'échelle pour la hauteur
                        radius=5000,                  # Rayon des colonnes en mètres
                        get_fill_color='[255, 140, 0, 200]',  # Couleur orange avec transparence
                        pickable=True,
                        extruded=True,
                        auto_highlight=True,
                    ),
                ],
                tooltip={
                    'html': '<b>Département:</b> {departement}<br/><b>Nombre:</b> {nb}',
                    'style': {
                        'backgroundColor': 'steelblue',
                        'color': 'white'
                    }
                }
            ))
