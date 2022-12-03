from tokenize import group
import pandas as pd
import numpy as np
import json
from modelo.SentenTopicModel import Sententopic
from modelo.SententreeModel import Sententree
from flask import Flask, jsonify, render_template, request, redirect, url_for
import sys
import time

#df=pd.read_csv("data/#russiaResultado.csv",lineterminator='\n')
#df=pd.read_csv("data/#texasResultado.csv",lineterminator='\n')
df=pd.read_csv("data/#WWDCResultado.csv",lineterminator='\n')


start_time = time.time()
arbol=Sententopic(df,10)
print(f"Tiempo: {time.time() - start_time} segundos")


app = Flask(__name__)


@app.route('/')
def index():
    rawData=arbol.getDataJson()
    return render_template(
        "index.html",
        data=rawData
    )

@app.route('/crearSententree',methods=['POST'])
def crearSententree():
    if request.method != "POST":
        return

    escogidos=[int(i) for i in request.form.getlist('escogidos[]')]
    print(escogidos)
    for topico in escogidos:
        #print(f"activate {arbol.SententopicList[topico].activate}")
        arbol.SententreeList[topico].activate=not arbol.SententreeList[topico].activate
        #print(f"activate {arbol.SententopicList[topico].activate}")
    rawData=arbol.getDataJson()
    return rawData

@app.route('/eliminarNodo',methods=['POST'])
def eliminarNodo():
    if request.method != "POST":
        return
    escogidos=[int(i) for i in request.form.getlist('escogidos[]')]
    print(escogidos)
    for topico in escogidos:
        arbol.SententreeList[topico].visible=False
    rawData=arbol.getDataJson()
    return rawData

@app.route('/buscarTopicos',methods=['POST'])
def buscarTopicos():
    if request.method != "POST":
        return
    escogidos=[int(i) for i in request.form.getlist('escogidos[]')]
    numeroTopicos=request.form.get('numeroTopicos')
    for topico in escogidos:
        #arbol.SententreeList[topico].ocultar=True
        arbol.expandirNodo(topico,int(numeroTopicos))
        #arbol.SententreeList[topico].visible=False
    rawData=arbol.getDataJson()
    return rawData

@app.route('/mezclarTopicos',methods=['POST'])
def mezclarTopicos():
    if request.method != "POST":
        return
    escogidos=[int(i) for i in request.form.getlist('escogidos[]')]
    arbol.mezclarTopicos(escogidos)

    rawData=arbol.getDataJson()
    return rawData
if __name__ == '__main__':
    app.run(debug=True)
