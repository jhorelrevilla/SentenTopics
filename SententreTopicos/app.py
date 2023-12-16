from modelo.SentenTopicModel import Sententopic
from flask import Flask, render_template, request, redirect, url_for,json
import json
import time

WordsNumberPerSententree=3
files={
    "#WWDC":"data/#WWDCResultado.csv",
    "#Russia":"data/#russiaResultado.csv",
    "#Texas":"data/#texasResultado.csv"
}

start_time = time.time()


arbol=Sententopic(list(files.values())[0],WordsNumberPerSententree)
print(f"Tiempo: {time.time() - start_time} segundos")

# def verificarRequest(func):
#     def inner(request):
#         if request.method != "POST":
#             return     
#         func(request.form.getlist('escogidos[]'))
#         return arbol.getDataJson2()
#     return inner


app = Flask(__name__)
#-----------------------------------------------
@app.route('/cambiarDataset',methods=['POST'])
def cambiarDataset():
    if request.method != "POST":
        return
    dataSetName=str(request.form.get('dataSetName'))
    print(f"cambiar dataset {dataSetName}")
    print(f"con el archivo {files[dataSetName]}")
    arbol=Sententopic(files[dataSetName],WordsNumberPerSententree)

    rawData=arbol.getDataJson2()
    return rawData
#-----------------------------------------------
@app.route('/')
def index():

    return render_template(
        "index.html",
        # data=json.dumps(arbol.getDataJson2()),
        data=json.dumps(arbol.getDataJson2()),
        dataFiles=list(files.keys())
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
