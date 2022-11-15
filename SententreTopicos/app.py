from tokenize import group
import pandas as pd
import numpy as np
import json
from modelo.SentenTopicModel import Sententopic
from modelo.SententreeModel import Sententree
from flask import Flask, jsonify, render_template, request, redirect, url_for


df=pd.read_csv("data/#WWDCResultado.csv")
arbol=Sententopic(df,5)

topico=0
arbol2=Sententree(
    arbol.SententopicDfList[topico],
    1,
    arbol.topicList[topico],
    0)
    



#rawData=arbol2.getData()
#arbol.printSententopic()




rawData2 = {
    "nodes": [
        {"label": "0", "width": 60, "height": 40, "group":1},
        {"label": "1", "width": 60, "height": 40, "group":1},
        {"label": "el pepe", "width": 60, "height": 40, "group":1},
        {"label": "3", "width": 60, "height": 40, "group":1},
        {"label": "4", "width": 60, "height": 40, "group":1}
    ],
    "links": [
        {"source": 0, "target": 2},
        {"source": 1, "target": 2},
        {"source": 3, "target": 2},
        {"source": 2, "target": 4}
    ],
    "constraints": [
        {
            "axis":"x",
            "left":2,
            "right":1,
            "gap":30
        },
        {
            "axis":"x",
            "left":2,
            "right":4,
            "gap":30
        }
    ],
    "groups":[
        {"leaves":[0,1,2,3,4]}
    ]
}


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
        arbol.SententopicList[topico].activate=not arbol.SententopicList[topico].activate
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
        arbol.SententopicList[topico].visible=False
    rawData=arbol.getDataJson()
    return rawData
if __name__ == '__main__':
    app.run(debug=True)
