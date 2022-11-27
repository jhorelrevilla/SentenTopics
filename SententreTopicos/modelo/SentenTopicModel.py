

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
            parent=-1
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
                    parent=parent
                ))
    # -------------------------------------------------------

    def expandirNodo(self, SententreeID, numTopics):
        df = self.SententreeList[SententreeID].tokens.data.copy()
        if (df.shape[0] <= 50):
            return
        self.crearSententreePerTopics(
            df,
            numTopics,
            self.SententreeList[SententreeID].nodosListID[0])
    # -------------------------------------------------------

    def mezclarTopicos(self, nodosEscogidos):
        dfEscogidos = []
        nodoMenor = 999
        topicosEscogidos=[]
        print("PRIMERO")
        for nodo in nodosEscogidos:
            #juntar df
            dfEscogidos.append(self.SententreeList[nodo].tokens.data.copy())
            #buscar el nodo padre menor
            if (self.SententreeList[nodo].parent < nodoMenor):
                nodoMenor = self.SententreeList[nodo].parent
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
                parent=nodoMenor
            ))
        print("TERCERO")
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

    def getTopicList(self):
        return [["pay", "apple", "payment", "interest", "equal", "split", "0", "purchase", "week", "cost", "order", "klarna", "6", "wallet", "buy", "introducing", "4", "online", "directly", "tap", "allows", "tracking", "allow", "digital", "break", "info", "announces", "service", "challenge", "introduced"],
                ["keynote", "event", "day", "park", "today", "announcement", "tim", "craig", "watching", "morning", "cook", "join", "ready", "minute", "fun",
                    "excited", "started", "stuff", "developer", "special", "team", "stream", "coverage", "bit", "community", "year", "good", "person", "glass", "tweet"],
                ["lock", "screen", "font", "lockscreen", "clock", "widget", "wallpaper", "style", "bottom", "roll", "option", "io", "activity", "multiple", "message",
                    "notification", "customize", "change", "focus", "16", "edit", "customizable", "mark", "unread", "ios16", "live", "customization", "biggest", "imessages", "undo"],
                ["heart", "workout", "sleep", "rate", "zone", "afib", "medication", "history", "metric", "track", "watch", "#applewatch", "face", "health", "fitness",
                "tracking", "custom", "9", "siri", "drug", "#watchos9", "sensor", "reminder", "watchos", "running", "interaction", "form", "ui", "app", "calendar"],
                ["gpu", "transistor", "cpu", "5nm", "unified", "24gb", "memory", "25", "core", "performance", "medium", "billion", "faster", "10", "20",
                "m1", "#m2", "power", "gen", "announcing", "chip", "8", "18", "glance", "pc", "m2", "announces", "latest", "number", "processor"],
                ["safety", "location", "abusive", "domestic", "access", "relationship", "abuse", "reset", "check", "privacy", "personal", "sharing", "account", "data", "help",
                "setting", "people", "icloud", "case", "shared", "helpful", "family", "tool", "stop", "library", "content", "share", "allows", "photo", "automatically"],
                ["car", "cluster", "instrument", "carplay", "vehicle", "integration", "next-gen", "#carplay", "manufacturer", "late", "2023", "play", "speed", "entire", "industry",
                "ui", "control", "experience", "showing", "google", "level", "integrated", "seriously", "power", "building", "generation", "sneak", "powered", "pretty", "smart"],
                ["retina", "136", "liquid", "magsafe", "1080p", "pound", "charging", "speaker", "27", "notch", "port", "spatial", "thin", "18", "bezel",
                "audio", "inch", "display", "fast", "hour", "color", "battery", "high", "space", "keyboard", "charge", "min", "midnight", "charger", "colour"],
                ["window", "manager", "group", "spotlight", "safari", "search", "ventura", "multitasking", "mail", "tab", "metal", "stage", "desktop", "macos", "side", "collaboration",
                "continuity", "improved", "passkey", "facetime", "overlapping", "#macosventura", "desk", "freeform", "view", "shortcut", "front", "called", "handoff", "ipad"],
                ["macbook", "pro", "m2", "air", "13-inch", "education", "month", "#macbookpro", "13", "model", "1299", "price", "pricing", "india", "1199", "r", "start", "beta", "launch", "chip", "2022", "public", "starting", "14", "july", "fall", "release", "macbooks", "official", "#macbookair"]]
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
                "name": "-1",
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

        print(nodosID)

        #print("actualizar enlaces")
        # actualizar enlaces
        for link in links:

            source = nodosID.index(link['source'])
            target = nodosID.index(link['target'])
            #print(f"source {type(source)}")
            #print(f"target {target}")
            link['source'] = source
            link['target'] = target
            #print(f"link {link}")
        # actualizar constraits
        for restriccion in restricciones:
            if (len(restriccion) == 4):
                restriccion['left'] = nodosID.index(restriccion['left'])
                restriccion['right'] = nodosID.index(restriccion['right'])
                continue
            for offset in restriccion['offsets']:
                offset['node'] = nodosID.index(offset['node'])
            # print(restriccion)
        # crear enlaces del nodo
        for sententree in self.SententreeList:
            if not sententree.visible:
                continue
            nombreNodo = sententree.parent
            if (sententree.parent == -1):
                nombreNodo = "-1"

            #print(f"Sententopic source {nombreNodo}")
            #print(f"Sententopic target {sententree.nodosListID[0]}")
            links.append(
                {
                    "source": nodosID.index(nombreNodo),
                    "target": nodosID.index(sententree.nodosListID[0]),
                    "lenght": 300,
                    "tipo":"sententopic"
                }
            )
            restricciones.append(
                {
                    "axis": "x",
                    "left": nodosID.index(nombreNodo),
                    "right": nodosID.index(sententree.nodosListID[0]),
                    "gap": 200
                }
            )

        # actualizar grupos
        print("------------")
        for grupo in grupos:
            newNodes=[]
            for nodo in grupo['leaves']:
                newNodes.append(nodosID.index(nodo))
            grupo['leaves']=newNodes
            #grupo['leaves'] = [nodosID.index(nodo) for nodo in grupo['leaves']]
            

        result = {
            "nodes": nodos,
            "links": links,
            "constraints": restricciones,
            "groups": grupos
        }
        return result
