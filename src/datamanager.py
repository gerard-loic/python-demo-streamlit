import duckdb
import sys
sys.path.append('config')
import config
import streamlit as st
import math

class DataManager():
    def __init__(self):
        self.initCnx()
    
    def initCnx(self):
        print("Initialisation de la connexion")
        self.cnx = duckdb.connect()
        self.initData()

    @st.cache_resource
    def initData(_self):
        getdata = f"CREATE TABLE conseillers AS SELECT * FROM read_csv_auto('{config.CSV_URL}')"
        _self.cnx.execute(getdata)
        print("Données chargées")

    def getSexeRepartition(self):
        query = 'SELECT COUNT(*) AS nb, "Code sexe" AS sexe FROM conseillers GROUP BY "Code sexe"'
        result = self.cnx.execute(query).fetchdf()
        return result
    
    def getAgeRepartition(self):
        query = """SELECT COUNT(*) AS nb, age 
        FROM 
        (SELECT 
        date_diff('year', "Date de naissance", CURRENT_DATE) AS age FROM conseillers) AS ss
        GROUP BY age 
        ORDER BY age ASC"""
        result = self.cnx.execute(query).fetchdf()

        ranges = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ]
 
        #On récupère des tubles, on ignore la première valeur
        for _, row in result.iterrows():
            
            index = math.ceil(row['age']/10)-1
            if index > len(ranges)-1:
                index = len(ranges)-1
            ranges[index] = ranges[index] + row['nb']

        labels = []
        values = []

        for i in range(0, 8):
            labels.append(str(i*10+1)+"-"+str(i*10))
            values.append(int(ranges[i]))
        
        out = {"labels" : labels, "values" : values}

        return out