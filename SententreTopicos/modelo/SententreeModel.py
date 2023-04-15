from anytree import Node, RenderTree
import pandas as pd
from anytree.dotexport import RenderTreeGraph
from anytree.exporter import DotExporter
import json


class Sententree:
    def __init__(self, data, palabrasNecesarias, topic, numTopic,numTotalDf,tokens):
        """Variables para la construccion del modelo"""
        self.data = data        
        self.palabrasNecesarias=palabrasNecesarias
        self.topic = topic
        self.numTopic = numTopic

        # Tamanio max/min fuente
        self.maxFont = 200+((data.shape[0]*200)/numTotalDf)
        self.minFont = 90
        
        # Crea nodo raiz 
        allTweetsNode=Node("All tweets")
        allTweetsNode.seq=[]
        allTweetsNode.DB=[i for i in range(0,data.shape[0])]
        word,s0,s1=self.growSeqTopics(allTweetsNode)
        allTweetsNode=None
        # Si la palabra con mayor soporte es del topico
        if int(word) in self.topic:
            self.topic.remove(int(word))

        self.maxBdSize = len(s0)
        self.nodosListID=[f"{self.numTopic}-0"]

        self.nodoRaiz = Node(f"{word}")
        self.nodoRaiz.word = int(word)
        self.nodoRaiz.DB=list(s0)
        self.nodoRaiz.seq=[word]
        self.nodoRaiz.graphLinks = {word: f"{self.numTopic}-0"}
        self.nodoRaiz.graphNodes = [{
            "name": f"{self.numTopic}-0",
            "fontSize": self.maxFont,
            "label": word,
            "rawText": str(
                [self.data['tweet'][int(tweetId)] for tweetId in s0[:1]][0]    
            ),
            "likes_count":int(self.data['likes_count'][s0[:1][0]]),                         
            "rawTextID": s0[:1],
            "numTopic":self.numTopic,
            "size": len(s0),
            "width": 0,
            "height": 0    
            }]
        
        word=None
        s0=None
        s1=None

        print("-"*20)
        print(f"df total {data.shape[0]}")
        print(f"Sententree con un {len(self.nodoRaiz.DB)}")
        print(f"Con los topicos {topic}")
        print("-"*20)
        #print(f"topicos tokenizados {self.topic}")
        
        self.leafNodes = self.generacionPatrones(
            self.nodoRaiz, 
            palabrasNecesarias
            )

        self.convertirTokens(tokens)
    # ------------------------------------------------------------------------------------
    def convertirTokens(self,tokenizer):
        nodos=self.getNodes(True)
        for nodo in nodos:
            nodo['label']=str(tokenizer.token2word(int(nodo['label'])))
    # ------------------------------------------------------------------------------------
    def getNodoLargestSupport(self, leafNodes):
        pos = 0
        # busca el nodo con mayor cantidad de elementos
        for nodePos in range(len(leafNodes)):
            if (len(leafNodes[pos].DB) < len(leafNodes[nodePos].DB)):
                pos = nodePos
        result = leafNodes[pos]
        del leafNodes[pos]
        return result
    # ------------------------------------------------------------------------------------
    def growSeqTopics(self, s):
        s0 = []
        s1 = []
        bdDict = {}
        # Crea diccionario de todas las palabras
        for tweetId in s.DB:
            for token in self.data['tokens'][int(tweetId)].split():
                # evita palabras de la secuencia
                if token in s.seq:
                    continue
                if token in bdDict:
                    bdDict[token] += 1
                else:
                    bdDict[token] = 1
        # Crea diccionario de solo las palabras del topico
        topicDict = {}
        for wordTopic in self.topic:
            if wordTopic in bdDict:
                topicDict[wordTopic] = bdDict[wordTopic]
        # Escoge palabras del topico o de la BD completa 
        word = None
        if(len(topicDict)==0):
            # print(f"BdDict {len(bdDict)}")
            # print(f"topicDict {len(topicDict)}")
            word = str(max(bdDict, key=lambda x: bdDict[x]))
        else:
            word = str(max(topicDict, key=lambda x: topicDict[x]))
        # Dividir la BD
        for tweetId in s.DB:
            tweetTokens = self.data['tokens'][int(tweetId)].split()
            if word in tweetTokens:
                s0.append(tweetId)
            else:
                s1.append(tweetId)
        return word, list(s0), list(s1)
    # ------------------------------------------------------------------------------------
    def generacionPatrones(self, nodoRaiz, palabrasNecesarias):
        leafNodes = []
        leafNodes.append(nodoRaiz)

        while (palabrasNecesarias > 0 and leafNodes):
            # pop pattern with the largest support from leaf sequential patterns
            s = self.getNodoLargestSupport(leafNodes)
            newS0 = None
            newS1 = None
            if (not s.children):
                # Find the most frequent super sequences s' of s that is exactly one word longer than s;

                word, s0, s1 = self.growSeqTopics(s)
                # print('-'*10)
                # print(f"escoge la palabra  token {word}")
                # print(f"s0 contiene {len(s0)}")
                # print(f"s1 contiene {len(s1)}")
                # print(f"seq {s.seq}")
                # print(f"Top Tweets {s0[:2]}")
                # print('-'*10)


                # Crea el nodo s0(palabra) y s1(sin palabra)
                # Agrega s0 como hijo izq

                # palabraCorpus = list(self.data.itemset.keys())[int(word)]
                # newS0 = Node(f"{palabraCorpus}({len(s0)})", parent=s)
                newS0 = Node(f"{word}({len(s0)})", parent=s)
                newS0.word=int(word)
                newS0.DB = s0
                newS0.seq = list(s.seq)
                newS0.seq.append(word)
                """ CREAR NODOS PARA EL GRAFO"""
                newS0.graphNodes = list(s.graphNodes)

                fontSize = ((self.maxFont*len(s0))/self.maxBdSize)
                if fontSize < self.minFont:
                    fontSize += self.minFont
                # self.data.data['data'][int(tweetId)]
                topTweets = [self.data['tweet']
                             [int(tweetId)] for tweetId in s0[:1]]

                nodoJson = {
                    "name": f"{self.numTopic}-{palabrasNecesarias}",
                    "fontSize": fontSize,
                    "label": word,
                    "rawText": str(topTweets[0]),
                    "rawTextID": s0[:1],
                    "numTopic":self.numTopic,
                    "likes_count":int(self.data['likes_count'][s0[:1][0]]),
                    "size": len(s0),
                    "width": 0,
                    "height": 0
                }
                self.nodosListID.append(
                    f"{self.numTopic}-{palabrasNecesarias}")
                newS0.graphNodes.append(nodoJson)
                """ CREAR ARISTAS PARA EL GRAFO"""
                newS0.graphLinks = dict(s.graphLinks)
                newS0.graphLinks[word] = f"{self.numTopic}-{palabrasNecesarias}"

                # Agrega s1 como hijo derecho
                newS1 = Node(f"nodo nulo({len(s1)})", parent=s)
                newS1.DB = s1
                newS1.seq = list(s.seq)
                newS1.graphNodes = list(s.graphNodes)
                newS1.graphLinks = dict(s.graphLinks)

            palabrasNecesarias -= 1
            # push s' and s to leaf sequential patterns
            if (newS0 and newS1):
                leafNodes.append(newS0)
                leafNodes.append(newS1)
            # print("-------------------------")
        return leafNodes
    # ------------------------------------------------------------------------------------
    def getNodePos(self, node):
        return self.nodosListID.index(node)+(self.numTopic*(self.palabrasNecesarias+1))
    # ------------------------------------------------------------------------------------
    def getData(self):
        nodos = self.getNodes()
        links = self.getLinks()
        restricciones = self.getRestricciones()
        grupos = self.getGrupos()

        result = {
            "nodes": nodos,
            "links": links,
            "constraints": restricciones,
            "groups": grupos
        }
        return result
    # ------------------------------------------------------------------------------------
    def getGrupos(self,visible:bool):
        if not visible:
            return [
                {
                    "leaves": [self.nodosListID[0]],
                    "grupo":self.numTopic,
                    "escogido":0
                }
            ]
        return [
            {
                "leaves": self.nodosListID,
                "grupo":self.numTopic,
                "escogido":0
            }
        ]
    # ------------------------------------------------------------------------------------
    def romperCiclos(self,grafo,nodo,visitados,ciclo):
        #print("-"*5)
        #print(f"visitando {nodo}")
        if nodo not in grafo:
            return False
        visitados.append(nodo)
        #print(f"recorrer {grafo[nodo]}")

        for links in grafo[nodo]:
            if(links in visitados):
                return True
            if(self.romperCiclos(grafo,links,visitados,ciclo)):
                ciclo[nodo]=links
            """
            if links in visitados:
                print(f"{links} esta en {visitados}")
                print(f"eliminando a {links}")
                enlaces=list(grafo[nodo])
                enlaces.remove(links)
                grafo[nodo]=enlaces
                print(f"'{nodo}': {grafo[nodo]}")
            """
    # ------------------------------------------------------------------------------------
    def getLinks(self, visible:bool):
        result = []
        dicSeq = {}
        grafo={}
        secuencias = []
        # extraer secuencias
        if not visible:
            return []

        for leaf in self.leafNodes:
            secuencia = []
            pointer = leaf
            if (pointer.name.find("nodo nulo") != -1):
                continue
            while (pointer.parent):
                if (pointer.name.find("nodo nulo") != -1):
                    pointer = pointer.parent
                    continue
                secuencia.append(pointer)
                pointer = pointer.parent
            secuencia.append(pointer)

            secuencias.append(secuencia)

        #for seq in secuencias:
        #    for word in seq:
        #        print(f"{word.name}  ", end="")
        #    print("")

        for secuencia in secuencias:
          #print("-----------------")
          #print(f"palabra {secuencia[0].name}") 
          listPalabras=[ str(i.word) for i in secuencia]
          topTweetId = secuencia[0].graphNodes[-1]['rawTextID'][0]
        #   ['tweetFiltrado'][int(tweetId)]
        
          topTweet = self.data['tokens'][int(topTweetId)].split()
        #  topTweet=self.data.iloc[3]['tweetFiltrado']

          #print(f"listPalabras {listPalabras}")
        #   print (f"topTweet {topTweet}")
          
          tempo = {}

          # recorre la secuencia y ordena las palabras en el orden que aparecen
          for palabra in listPalabras:
            tempo[palabra] = topTweet.index(palabra)
          #print(f"tempo {tempo}")
          tempo = {k: v for k, v in sorted(
            tempo.items(), key=lambda item: item[1])}
          #print(f"orden que aparecen {tempo}")
          #print(secuencia[0].graphLinks)

          
          for word in range(1,len(listPalabras)):
            source = list(tempo.keys())[word-1]
            source = secuencia[0].graphLinks[source]

            target = list(tempo.keys())[word]
            target = secuencia[0].graphLinks[target]

            if source not in grafo:
              grafo[source] = [target]
            else:
              if target not in grafo[source]:
                grafo[source].append(target)
        #-------------elimina ciclos
        #print("*"*10)
        #print(f"grafo\n{grafo}")
        

        #print(f"NUEVO GRAFO\n{self.romperCiclos(grafo,list(grafo.keys())[0],[],ciclos)} ")
        
        for k in grafo.keys():
            ciclos={}
            self.romperCiclos(grafo,k,[],ciclos)
            #print(f"ciclos {ciclos}")
            for k,v in ciclos.items():
                lista=list(grafo[k])
                #print(f"lista {lista}")
                lista.remove(v)
                grafo[k]=lista
        #-------------genera enlaces a partir del grafo
        for k, v in grafo.items():
          for target in v:
                result.append({
                    "source": k,
                    "target": target,
                    "tipo":"sententree"
                })
        #print(f"result {result}")
        #print("####################################################"
        return result
    # ------------------------------------------------------------------------------------
    def getRestricciones(self,visible:bool):
        result = []
        restriccionXSource = {}
        restriccionXTarget = {}

        if not visible:
            return []
        for link in self.getLinks(True):
            constrait = {
                "left": link["source"],
                "right": link["target"],
                "tipo":"sententree"
            }
            result.append(constrait)
            if (link['source'] in restriccionXSource):
                restriccionXSource[link['source']].append(link['target'])
            else:
                restriccionXSource[link['source']] = [link['target']]

            if (link['target'] in restriccionXTarget):
                restriccionXTarget[link['target']].append(link['source'])
            else:
                restriccionXTarget[link['target']] = [link['source']]
        #print(restriccionXSource)
        #print(restriccionXTarget)
        return result
    # ------------------------------------------------------------------------------------
    def getNodes(self,visible:bool):
        nodosDict = []
        result = []
        if not visible:
            return self.nodoRaiz.graphNodes

        for seq in self.leafNodes:
            if (len(seq.seq)) >= 1:
                for nodo in seq.graphNodes:
                    if nodo['name'] not in nodosDict:
                        result.append(nodo)
                        nodosDict.append(nodo['name'])
                    else:
                        continue
        return result
    # ------------------------------------------------------------------------------------
    def printSententree(self):
        print(f"Nodo principal {self.nodosListID[0]}")
        for nodo in self.nodosListID:
            print(nodo)
        print("######################################")