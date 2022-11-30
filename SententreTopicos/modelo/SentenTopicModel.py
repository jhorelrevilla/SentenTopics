

import pandas as pd
from modelo.SententreeModel import Sententree
from modelo.seanmfTopic import extractTopics
import json


class Sententopic:
    def __init__(self, dataDf, numPalabrasPerTopic):
        self.SententreeList = list()
        self.numPalabrasPerTopic = numPalabrasPerTopic
        self.crearSententreePerTopics(
            df=dataDf,
            numTopics=10,
            parent='root' 
        )
        """
        self.topicList = self.getTopicList()
        self.numPalabrasPerTopic = numPalabrasPerTopic
        dataDf['topico'] = dataDf.apply(
            lambda x: self.dividirDfTopicos(x.tweetFiltrado, topicList), axis=1)

        self.SententopicDfList = self.createSententopicDf(dataDf)
        self.SententreeList = []

        for i in range(len(self.SententopicDfList)):
            self.SententreeList.append(
                Sententree(
                    dataDf=self.SententopicDfList[i],
                    palabrasNecesarias=numPalabrasPerTopic,
                    topic=self.topicList[i],
                    numTopic=i,
                    parent=-1
                ))
        """
    # -------------------------------------------------------

    def crearSententreePerTopics(self, df, numTopics, parent):
        numTweets=df.shape[0]
        print(f"numTweets {numTweets}")
        data = df['tweetFiltrado'].to_list()
        topicList = extractTopics(data, numTopics)

        df['topico'] = df.apply(
            lambda x: self.dividirDfTopicos(
                x.tweetFiltrado,
                topicList
            ), axis=1)

        dfList = self.createSententopicDf(df, len(topicList))
        # for i in dfList:
        #  print(f"{i.shape[0]}")

        for i in range(len(dfList)):
            self.SententreeList.append(
                Sententree(
                    dataDf=dfList[i],
                    palabrasNecesarias=self.numPalabrasPerTopic,
                    topic=topicList[i],
                    numTopic=len(self.SententreeList),
                    parent=parent,
                    numTotalDf=numTweets
                ))
    # -------------------------------------------------------

    def expandirNodo(self, SententreeID, numTopics):
        df = self.SententreeList[SententreeID].tokens.data.copy()
        if (df.shape[0] <= 50):
            return
        self.SententreeList[SententreeID].activate=False
        self.crearSententreePerTopics(
            df,
            numTopics,
            self.SententreeList[SententreeID].nodosListID[0])
    # -------------------------------------------------------
    def getNumeroTopico(self,nodo):
        if (self.SententreeList[nodo].parent =="root"):
            return -1
        else:
            return int(str(self.SententreeList[nodo].parent).split('-')[0])

    # -------------------------------------------------------
    def mezclarTopicos(self, nodosEscogidos):
        dfEscogidos = []
        nodoMenor = self.getNumeroTopico(nodosEscogidos[0])
        topicosEscogidos=[]
        print("PRIMERO")

        for nodo in nodosEscogidos:
            #juntar df
            dfEscogidos.append(self.SententreeList[nodo].tokens.data.copy())
            #buscar el nodo padre menor
            print(f"PADRE {self.SententreeList[nodo].parent}")
            nodoPadre=self.getNumeroTopico(nodo)

            print(f"nodoPadre {type(nodoPadre)} -> {nodoPadre}")
            print(f"nodoMenor {type(nodoMenor)} -> {nodoMenor}")

            if (nodoPadre < nodoMenor):
                nodoMenor = nodoPadre



            #juntar topicos
            for palabra in self.SententreeList[nodo].rawTopic:
                if(palabra in topicosEscogidos):
                    continue
                topicosEscogidos.append(palabra)
            #ocultar topico
            self.SententreeList[nodo].visible=False

        dfMezclado = pd.concat(dfEscogidos)
        dfMezclado.reset_index(drop=True, inplace=True)
        dfMezclado.sort_values(by=['likes_count'], ascending=False)
        self.SententreeList.append(
            Sententree(
                dataDf=dfMezclado,
                palabrasNecesarias=self.numPalabrasPerTopic,
                topic=topicosEscogidos,
                numTopic=len(self.SententreeList),
                parent=self.SententreeList[nodoMenor].parent,
                numTotalDf=dfMezclado.shape[0]
            ))
        #print("TERCERO")
        for nodo in range(len(self.SententreeList)-1):
            if self.SententreeList[nodo].parent in nodosEscogidos:
                self.SententreeList[nodo].parent=len(self.SententreeList)-1
    # -------------------------------------------------------

    def dividirDfTopicos(self, tweet, topicList):
        resultTopics = []
        for topic in topicList:
            numPalabras = 0
            for word in tweet.split():
                if word in topic:
                    numPalabras += 1
            if numPalabras == 0:
                resultTopics.append(-1)
                continue
            resultTopics.append(float(numPalabras/len(topic)))
        return resultTopics.index(max(resultTopics))
    # -------------------------------------------------------
    def createSententopicDf(self, df, numTopics):
        result = []
        for topic in range(numTopics):
            topicDf = df.loc[df['topico'] == topic]
            #print(f"topico {topic} tienen {topicDf.shape}")
            topicDf.reset_index(drop=True, inplace=True)
            result.append(topicDf.copy())
        return result
    # -------------------------------------------------------

    def printSententopic(self):
        for tree in self.SententreeList:
            tree.printSententree()
    # -------------------------------------------------------

    def getDataJson(self):
        nodosID = []
        nodos = []
        links = []
        restricciones = []
        grupos = []

        # Nodo principal
        nodos.append(
            {
                "label": " ",
                "name": "Sententopic",
                "width": 60,
                "heigth": 40
            }
        )
        # nodos de los Sententree
        for sententree in self.SententreeList:
            if not sententree.visible:
                continue
            nodos.extend(sententree.getNodes())
            links.extend(sententree.getLinks())
            restricciones.extend(sententree.getRestricciones())
            grupos.extend(sententree.getGrupos())

        for nodo in nodos:
            nodosID.append(nodo['name'])

        # LINKS Y RESTRICCIONES DEL SENTENTOPIC
        sententopicLinks=[]
        SententopicRestricciones=[]
        for sententree in self.SententreeList:
            if not sententree.visible:
                continue
            nombreNodo = sententree.parent
            if (sententree.parent == 'root'):
                nombreNodo = "Sententopic"

            #print(f"Sententopic source {nombreNodo}")
            #print(f"Sententopic target {sententree.nodosListID[0]}")
            sententopicLinks.append(
                {
                    "source": nodosID.index(nombreNodo),
                    "target": nodosID.index(sententree.nodosListID[0]),
                    "length": 0,
                    "tipo":"sententopic"
                }
            )
            
            SententopicRestricciones.append(
                {
                    "axis": "x",
                    "left": nodosID.index(nombreNodo),
                    "right": nodosID.index(sententree.nodosListID[0]),
                    "tipo": "sententopic",
                    "gap":300
                }
            )
            
        # LINKS Y RESTRICCIONES DEL SENTENTREE
        for link in links:
            source = nodosID.index(link['source'])
            target = nodosID.index(link['target'])
            #print(f"source {type(source)}")
            #print(f"target {target}")
            link['source'] = source
            link['target'] = target
            link['length'] = 120
            #link['gap']=30
            #print(f"link {link}")
        # restricciones
        for restriccion in restricciones:
            if('offset' in restriccion.keys()):
                for offset in restriccion['offsets']:
                    offset['node'] = nodosID.index(offset['node'])
            
            restriccion['axis'] = "x"
            restriccion['left'] = nodosID.index(restriccion['left'])
            restriccion['right'] = nodosID.index(restriccion['right'])
            restriccion['gap']=150
        #--------------------------------------------------------------------
        # actualizar grupos
        for grupo in grupos:
            newNodes=[]
            for nodo in grupo['leaves']:
                newNodes.append(nodosID.index(nodo))
            grupo['leaves']=newNodes
            grupo['padding']=5
            #grupo['leaves'] = [nodosID.index(nodo) for nodo in grupo['leaves']]
            
        links+=sententopicLinks
        restricciones+=SententopicRestricciones
        result = {
            "nodes": nodos,
            "links": links,
            "constraints": restricciones,
            "groups": grupos
        }
        return result
