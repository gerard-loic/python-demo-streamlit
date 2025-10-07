from config.config import Config
from src.datamanager import DataManager
from src.appmanager import AppManager
import streamlit as st
import plotly.express as px



#streamlit run app.py

#Initialisation du gestionnaire de données
dm = DataManager()

#gestion de l'interface de l'application
app = AppManager(dm)

