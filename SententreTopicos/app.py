import pandas as pd
import numpy as np
import json
from modelo.SentenTopicModel import Sententopic
from modelo.SententreeModel import Sententree
from flask import Flask, jsonify, render_template


df=pd.read_csv("data/#WWDCResultado.csv")
arbol=Sententopic(df,0)

arbol2=Sententree(
    arbol.SententopicDfList[0],
    10,
    arbol.topicList[0],
    0)


rawData=arbol.getDataJson()
#rawData=arbol2.getData()
#



"""
rawData = {
    "nodes": [
        {"name": "jhorel", "width": 60, "height": 40},
        {"name": "bebe", "width": 60, "height": 40},
        {"name": "casa", "width": 60, "height": 40},
        {"name": "dedo", "width": 60, "height": 40},
        {"name": "enano", "width": 60, "height": 40}
    ],
    "links": [
        {"source": 0, "target": 2},
        {"source": 2, "target": 1},
        {"source": 2, "target": 3},
        {"source": 1, "target": 4}
    ],
    "constraints": [
        {
            "type": "alignment",
            "axis": "x",
            "offsets": [
                    {"node": 1, "offset": 0},
                    {"node": 3, "offset": 0}
            ]
        }
    ]
}
"""

app = Flask(__name__)


@app.route('/')
def index():
    #data = ["holi"]
    return render_template(
        "index.html",
        data=rawData
    )


if __name__ == '__main__':
    app.run(debug=True)
