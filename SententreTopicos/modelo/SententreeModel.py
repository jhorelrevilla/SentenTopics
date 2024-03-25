from anytree import Node, RenderTree
import pandas as pd
from anytree.dotexport import RenderTreeGraph
from anytree.exporter import DotExporter
import json
"""

"""

class Sententree:
    def __init__(self, data, topic, numTopic,tokens):
        """Variables para la construccion del modelo"""
        self.data = data        
        # self.palabrasNecesarias=num_words
        self.topic = topic
        self.numTopic = numTopic
        
        # Tamanio max/min fuente
        # self.maxFont = 200+((data.shape[0]*200)/numTotalDf)
        # self.minFont = 90
        self.maxFont = 1
        self.minFont = 1
        
        
        # Get the most relevant word and their db
        word,s0,s1=self.growSeqTopics(
            Node(
                "All tweets",
                seq=[],
                DB=[i for i in range(0,data.shape[0])]
            )
        )

        self.word=word
        
        
        self.maxBdSize = len(s0)
        self.nodosListID=[f"{self.numTopic}-0"]

        self.nodoRaiz = Node(f"{word}")
        self.nodoRaiz.word = int(word)
        self.nodoRaiz.DB=list(s0)
        self.nodoRaiz.seq=[word]
        self.nodoRaiz.graphLinks = {word: f"{self.numTopic}-0"}
        self.nodoRaiz.graphNodes = [{
            "name": f"{self.numTopic}-0",
            # "fontSize": self.maxFont,
            "label": str(tokens.token2word(int(word))),
            "rawText": str(
                [self.data['tweet'][int(tweetId)] for tweetId in s0[:1]][0]    
            ),
            "likes_count":int(self.data['likes_count'][s0[:1][0]]),                         
            "rawTextID": s0[:1],
            "numTopic":self.numTopic,
            "size": len(s0)
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
        
        # self.leafNodes = self.generacionPatrones(
        #     self.nodoRaiz, 
        #     palabrasNecesarias,
        #     tokens=tokens
        #     )

        # self.convertirTokens(tokens)
    # ------------------------------------------------------------------------------------
    # def convertirTokens(self,tokenizer):
    #     nodos=self.getNodes(True)
    #     for nodo in nodos:
    #         nodo['label']=str(tokenizer.token2word(int(nodo['label'])))
    # ------------------------------------------------------------------------------------
    # Consigue el nodo con mas apoyo
    def getNodoLargestSupport(self, leafNodes):
        pos = 0
        # Compara las hojas del arbol
        for nodePos in range(len(leafNodes)):
            if (len(leafNodes[pos].DB) < len(leafNodes[nodePos].DB)):
                pos = nodePos
        # retornal la hoja con mas apoyo y la elimina del array
        result = leafNodes[pos]
        del leafNodes[pos]
        return result
    # ------------------------------------------------------------------------------------
    def growSeqTopics(self, s):
        s0 = []
        s1 = []
        bd_dict = {}
        # Count tokens in DB
        for tweet_id in s.DB:
            for token in self.data['tokens'][int(tweet_id)].split():
                # avoid repeat words in sequence
                if token in s.seq:
                    continue
                if token in bd_dict:
                    bd_dict[token] += 1
                else:
                    bd_dict[token] = 1
        # Create a Dictionary if topic exist in db_dict
        topic_dict={x:bd_dict.get(x,-1) for x in self.topic if bd_dict}
        # Escoge palabras del topico o de la BD completa 
        word = None
        if not topic_dict:
            word = max(bd_dict, key=lambda x: bd_dict[x])
        else:
            word = max(topic_dict, key=lambda x: topic_dict[x])
            self.topic.remove(word)
        # Dividir la BD
        for tweet_id in s.DB:
            tweetTokens = self.data['tokens'][int(tweet_id)].split()
            if str(word) in tweetTokens:
                s0.append(tweet_id)
            else:
                s1.append(tweet_id)
        return str(word), s0, s1
    # ------------------------------------------------------------------------------------
    def generacionPatrones(self, node_list, neededWords, tokens):
        leafNodes=[]
        leafNodes+=node_list

        while neededWords > 0 and leafNodes:
            # pop pattern with the largest support from leaf sequential patterns
            s = self.getNodoLargestSupport(leafNodes)
            newS0 = None
            newS1 = None
            if not s.children:
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
                # DESCARTADO
                # fontSize = ((self.maxFont*len(s0))/self.maxBdSize)
                # if fontSize < self.minFont:
                #     fontSize += self.minFont
                # DESCARTADO
                
                # self.data.data['data'][int(tweetId)]
                topTweets = [self.data['tweet'][int(tweetId)] for tweetId in s0[:1]]
                self.nodosListID.append(
                    f"{self.numTopic}-{neededWords}")
                newS0.graphNodes.append(
                    {
                        "name": f"{self.numTopic}-{neededWords}",
                        # "fontSize": fontSize,
                        "label": str(tokens.token2word(int(word))),
                        "rawText": str(topTweets[0]),
                        "rawTextID": s0[:1],
                        "numTopic":self.numTopic,
                        "likes_count":int(self.data['likes_count'][s0[:1][0]]),
                        "size": len(s0),
                    }
                )
                """ CREAR ARISTAS PARA EL GRAFO"""
                newS0.graphLinks = dict(s.graphLinks)
                newS0.graphLinks[word] = f"{self.numTopic}-{neededWords}"

                # Agrega s1 como hijo derecho
                newS1 = Node(f"nodo nulo({len(s1)})", parent=s)
                newS1.DB = s1
                newS1.seq = list(s.seq)
                newS1.graphNodes = list(s.graphNodes)
                newS1.graphLinks = dict(s.graphLinks)

            neededWords -= 1
            # push s' and s to leaf sequential patterns
            if newS0 and newS1:
                leafNodes.append(newS0)
                leafNodes.append(newS1)
            # print("-------------------------")
        return leafNodes
    # ------------------------------------------------------------------------------------
    # def getNodePos(self, node):
    #     return self.nodosListID.index(node)+(self.numTopic*(self.palabrasNecesarias+1))
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