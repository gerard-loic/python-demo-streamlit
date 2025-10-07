import duckdb
from config.config import Config
import streamlit as st
import math
import pandas as pd

"""
"Code du département",
"Libellé du département",
"Code de la collectivité à statut particulier",
"Libellé de la collectivité à statut particulier",
"Code de la commune",
"Libellé de la commune",
"Nom de l'élu",
"Prénom de l'élu",
"Code sexe",
"Date de naissance",
"Code de la catégorie socio-professionnelle",
"Libellé de la catégorie socio-professionnelle",
"Date de début du mandat",
"Libellé de la fonction",
"Date de début de la fonction",
"Code nationalité"
"""

class DataManager():
    def __init__(self):
        self.initCnx()
    
    def initCnx(self):
        print("Initialisation de la connexion")
        self.cnx = duckdb.connect()
        self.initData()


    def initData(_self):
        getdata = f"CREATE TABLE conseillers AS SELECT * FROM read_csv_auto('{Config.CSV_URL}')"
        _self.cnx.execute(getdata)
        print("Données chargées")

    @st.cache_resource
    def getSexeRepartition(_self, departement : str, fonction : str):
        query = 'SELECT COUNT(*) AS nb, "Code sexe" AS sexe FROM conseillers WHERE 1+1 '
        if departement != "--Tous--":
            query = query + f"AND \"Libellé du département\"='{departement}'" 
        if fonction != "--Tous--":
            query = query + f"AND \"Libellé de la fonction\"='{fonction}'"
        query = query + ' GROUP BY "Code sexe" ORDER BY "Code sexe"' 
        result = _self.cnx.execute(query).fetchdf()

        return result
    
    @st.cache_resource
    def getDepartements(_self):
        query = 'SELECT DISTINCT "Libellé du département" AS libelle FROM conseillers ORDER BY "Libellé du département" ASC'
        result = _self.cnx.execute(query).fetchdf()

        line_tous = pd.DataFrame({'libelle' : ['--Tous--']})
        return pd.concat([line_tous, result], ignore_index=True)
    
    @st.cache_resource
    def getFonctions(_self):
        query = 'SELECT DISTINCT "Libellé de la fonction" AS libelle FROM conseillers ORDER BY "Libellé de la fonction" ASC'
        result = _self.cnx.execute(query).fetchdf()

        line_tous = pd.DataFrame({'libelle' : ['--Tous--']})
        return pd.concat([line_tous, result], ignore_index=True)
    
    @st.cache_resource
    def getGeodispersion(_self, departement : str, fonction : str):
        query = 'SELECT COUNT(*) AS nb, "Code du département" AS departement FROM conseillers WHERE 1=1 '
        if departement != "--Tous--":
            query = query + f"AND \"Libellé du département\"='{departement}'" 
        if fonction != "--Tous--":
            query = query + f"AND \"Libellé de la fonction\"='{fonction}'"
        query = query + ' GROUP BY "Code du département"' 
        result = _self.cnx.execute(query).fetchdf()

        result['lat'] = None
        result['long'] = None

        for index, row in result.iterrows():
            if row["departement"] in Config.DEPARTEMENTS:
                result.at[index, 'lat'] = Config.DEPARTEMENTS[row["departement"]]["latitude"]
                result.at[index, 'long'] = Config.DEPARTEMENTS[row["departement"]]["longitude"]

        return result

    @st.cache_resource
    def getCspRepartition(_self, departement : str, fonction : str):
        query = """
        SELECT *
        FROM (
        SELECT COUNT(*) AS nb, "Libellé de la catégorie socio-professionnelle" as csp
        FROM 
        conseillers 
        WHERE 1=1
        """
        if departement != "--Tous--":
            query = query + f"AND \"Libellé du département\"='{departement}'" 
        if fonction != "--Tous--":
            query = query + f"AND \"Libellé de la fonction\"='{fonction}'"

        query += """
        GROUP BY "Libellé de la catégorie socio-professionnelle"
        ) AS ss 
        WHERE nb > 0 
        ORDER BY nb DESC  
        LIMIT 30
        """
        result = _self.cnx.execute(query).fetchdf()

        labels = []
        values = []
        for _, row in result.iterrows():
            labels.append(row["csp"])
            values.append(row["nb"])
        return {"labels" : labels[::-1], "values" : values[::-1]}


    @st.cache_resource
    def getAgeRepartition(_self, departement : str, fonction : str, sexe = None):
        query = """SELECT COUNT(*) AS nb, age 
        FROM 
        (SELECT 
        date_diff('year', "Date de naissance", CURRENT_DATE) AS age FROM conseillers 
        WHERE 1=1 
        """
        if sexe != None:
            query += f" AND \"Code sexe\"='{sexe}' "
        if departement != "--Tous--":
            query = query + f"AND \"Libellé du département\"='{departement}'" 
        if fonction != "--Tous--":
            query = query + f"AND \"Libellé de la fonction\"='{fonction}'"

        query += """ ) AS ss 
        GROUP BY age
        ORDER BY age ASC"""
        result = _self.cnx.execute(query).fetchdf()

        ranges = []

        for i in range(0, int(100/5)):
            ranges.append(0)
 
        #On récupère des tubles, on ignore la première valeur
        for _, row in result.iterrows():
            index = math.ceil(row['age']/5)-1
            if index > len(ranges)-1:
                index = len(ranges)-1
            ranges[index] = ranges[index] + row['nb']

        labels = []
        values = []

        for i in range(0, int(100/5)):
            labels.append(str(str(i*5+1)+" - "+str(i*5)))
            values.append(int(ranges[i]))
        out = {"labels" : labels, "values" : values}

        return out