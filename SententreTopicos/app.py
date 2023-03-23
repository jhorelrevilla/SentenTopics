from tokenize import group
import pandas as pd
import numpy as np
import json
from modelo.SentenTopicModel import Sententopic
from modelo.SententreeModel import Sententree
from flask import Flask, jsonify, render_template, request, redirect, url_for
from modelo.Tokenizer import Tokenizer
import sys
import time

#df=pd.read_csv("data/#russiaResultado.csv",lineterminator='\n')
#df=pd.read_csv("data/#texasResultado.csv",lineterminator='\n')
df=pd.read_csv("data/#WWDCResultado.csv",lineterminator='\n')


start_time = time.time()
#Tokenizar y ordenar el DF

arbol=Sententopic(df,3)
print(f"Tiempo: {time.time() - start_time} segundos")

def verificarRequest(func):
    def inner(request):
        if request.method != "POST":
            return     
        func(request.form.getlist('escogidos[]'))
        return arbol.getDataJson2()
    return inner
app = Flask(__name__)
#-----------------------------------------------
@app.route('/')
def index():
    return render_template(
        "index.html",
        data=arbol.getDataJson2()
    )
#-----------------------------------------------
@app.route('/crearSententree',methods=['POST'])
def crearSententree():
    if request.method != "POST":
        return

    arbol.activarNodos(request.form.getlist('escogidos[]'))
    
    rawData=arbol.getDataJson2()
    return rawData
#-----------------------------------------------
@app.route('/eliminarNodo',methods=['POST'])
def eliminarNodo():
    if request.method != "POST":
        return
    
    arbol.eliminarNodo(request.form.getlist('escogidos[]'))
    
    rawData=arbol.getDataJson2()
    return rawData
#-----------------------------------------------
@app.route('/buscarTopicos',methods=['POST'])
def buscarTopicos():
    if request.method != "POST":
        return
    nodos=request.form.getlist('escogidos[]')
    numero_topicos=int(request.form.get('numeroTopicos'))
    
    arbol.expandirNodo(nodos,numero_topicos)

    rawData=arbol.getDataJson2()
    return rawData
#-----------------------------------------------
@app.route('/mezclarTopicos',methods=['POST'])
def mezclarTopicos():
    if request.method != "POST":
        return

    escogidos=request.form.getlist('escogidos[]')
    arbol.mezclarTopicos(escogidos)

    rawData=arbol.getDataJson2()
    return rawData

if __name__ == '__main__':
    app.run(debug=True)
