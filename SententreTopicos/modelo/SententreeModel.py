from anytree import Node,RenderTree
import pandas as pd
from anytree.dotexport import RenderTreeGraph
from anytree.exporter import DotExporter
import json

"""-----------------------------------------------------"""
class Tokenize:
  def __init__(self,df):
    #diccionario de todos los tokens unicos
    self.itemset=self.getItemset(df)
    self.data=df[['tweet','tweetFiltrado','likes_count']].copy()
    #convierte el tweet en una serie de tokens
    self.data['tokens']=self.data['tweetFiltrado'].apply(lambda x:self.tokenizeTweet(str(x),self.itemset))
  def getItemset(self,BD):
    result={}
    contador=0
    for tweet in BD['tweetFiltrado'].values.tolist():
      for word in tweet.split():
        if(word in result):
          continue;
        else:
          result[word]=contador
          contador+=1
    return result
  def tokenizeTweet(self,tweet,tokenDict):
    result=[]
    for word in tweet.split():
      result.append(str(tokenDict[word]))
    return  ' '.join(result)
"""-----------------------------------------------------"""
class Sententree:
    def __init__(self,dataDf,palabrasNecesarias,topic,topicId):
        self.tokens=Tokenize(dataDf)
        #rawTopic=self.getTopic(numTopic)
        self.topic=self.tokenizarTopic(topic)
        self.numTopic=topicId
        #nodo=getNodo
        #crear nodo a partir de la palabra con mayor apoyo
        self.nodoRaiz=self.getNodeTopic(dataDf)
        #self.topic.remove(self.nodoRaiz.seq[0])
        self.leafNodes=self.generacionPatrones(self.nodoRaiz, palabrasNecesarias)
    #------------------------------------------------------------------------------------
    def getNodoLargestSupport(self,leafNodes):
        pos=0
        #busca la posicion del nodo con mayor cantidad de elementos en la DB
        for nodePos in range(len(leafNodes)):
            if(len(leafNodes[pos].DB) < len(leafNodes[nodePos].DB)):
                pos=nodePos
        result=leafNodes[pos]
        del leafNodes[pos]
        return result
    #------------------------------------------------------------------------------------
    def tokenizarTopic(self,rawTopic):
        result=[]
        for word in rawTopic:
            result.append(str(self.tokens.itemset[word]))
        return result
    #------------------------------------------------------------------------------------
    def growSeqTopics(self,s):
        s0=[]
        s1=[]
        bdDict={}  
        #cuenta el numero de token
        for tweetId in s.DB:
            for token in self.tokens.data['tokens'][int(tweetId)].split():
                if token in bdDict:
                    bdDict[token]+=1
                else:
                    bdDict[token]=1
        
        # Escoger palabras del topico
        word=None
        if(len(s.seq)>1):
          #evita palabras de la secuencia
          #print(f"tam seq {len(s.seq)}")
          if(len(s.seq)>0):
              for wordSeq in s.seq:
                if wordSeq in bdDict:
                  bdDict.pop(wordSeq)
          word=str(max(bdDict,key= lambda x: bdDict[x]))
        else:
          topicDict={}
          for wordTopic in self.topic:
              if wordTopic in bdDict:
                  topicDict[wordTopic]=bdDict[wordTopic]
          word=str(max(topicDict,key= lambda x: topicDict[x]))


        #divide la bd 
        for tweetId in s.DB:
            tweetTokens=self.tokens.data['tokens'][int(tweetId)].split()
            if word in tweetTokens:
                s0.append(tweetId)
            else:
                s1.append(tweetId)
        return word,list(s0),list(s1)
    #------------------------------------------------------------------------------------
    def generacionPatrones(self,nodoRaiz,palabrasNecesarias):
        leafNodes=[]
        leafNodes.append(nodoRaiz)

        while(palabrasNecesarias>0 and leafNodes):
            #pop pattern with the largest support from leaf sequential patterns
            s=self.getNodoLargestSupport(leafNodes)
            newS0=None
            newS1=None
            if(not s.children):
                #Find the most frequent super sequences s' of s that is exactly one word longer than s;
                #word,s0,s1=growSeq(s,tokens)
                word,s0,s1=self.growSeqTopics(s)
                """
                print(f"escoge la palabra {list(self.tokens.itemset.keys())[int(word)]} token {word}")
                print(f"s0 contiene {len(s0)}")
                print(f"s1 contiene {len(s1)}")
                print(f"seq {s.seq}")
                print(f"Top Tweets {s0[:2]}")
                """
                #crea el nodo s0(palabra) y s1(no palabra)
                #Agrega s0 como hijo izq 
                palabraCorpus=list(self.tokens.itemset.keys())[int(word)]
                newS0=Node(f"{palabraCorpus}({len(s0)})",parent=s)
                newS0.DB=s0
                newS0.seq=list(s.seq)
                newS0.seq.append(word)
                """ CREAR NODOS PARA EL GRAFO"""
                newS0.graphNodes=list(s.graphNodes)
                nodoJson={
                  "name":f"{self.numTopic}-{palabrasNecesarias}",
                  "fontSize":len(s0),
                  "label": palabraCorpus,
                  "rawText": s0[:5],
                  "width":100,
                  "height":80
                }
                newS0.graphNodes.append(nodoJson)
                """ CREAR ARISTAS PARA EL GRAFO"""
                newS0.graphLinks=dict(s.graphLinks)
                newS0.graphLinks[word]=f"{self.numTopic}-{palabrasNecesarias}"

                #Agrega s1 como hijo derecho
                newS1=Node(f"N/A({len(s1)})",parent=s)
                newS1.DB=s1
                newS1.seq=list(s.seq)
                newS1.graphNodes=list(s.graphNodes)
                newS1.graphLinks=dict(s.graphLinks)

            palabrasNecesarias-=1
            #push s' and s to leaf sequential patterns
            if(newS0 and newS1):
                leafNodes.append(newS0)
                leafNodes.append(newS1)
            #print("-------------------------")
        return leafNodes
    #------------------------------------------------------------------------------------
    def getNodeTopic(self, df):
        nodoRaiz=Node("All tweets")
        nodoRaiz.seq=[]

        nodoRaiz.DB=[i for i in range(0,df.shape[0])]

        word,s0,s1=self.growSeqTopics(nodoRaiz)

        self.topic.remove(word)
        

        palabraCorpus=list(self.tokens.itemset.keys())[int(word)]
        newNodo=Node(f"{palabraCorpus}")
        newNodo.id=0
        newNodo.DB=s0
        newNodo.seq=[word]
        nodoJson={
            "name":f"{self.numTopic}-0",
            "fontSize":len(s0),
            "label": list(self.tokens.itemset.keys())[int(word)],
            "rawText": s0[:5],
            "width":100,
            "height":50
        }
        newNodo.graphNodes=[nodoJson]
        newNodo.graphLinks={word:f"{self.numTopic}-0"}
        return newNodo
    #------------------------------------------------------------------------------------
    def getData(self):
      nodosID=[]

      nodos=self.getNodes()
      links=self.getLinks()
      restricciones=self.getRestricciones()

      for nodo in nodos:
        nodosID.append(nodo['name'])

      for link in links:
        link["source"]=nodosID.index(link["source"])
        link["target"]=nodosID.index(link["target"])

      for restriccion in restricciones:
        for offset in restriccion["offsets"]:
          offset["node"]=nodosID.index(offset["node"])

      result={
          "nodes":nodos,
          "links":links,
          "constraints":restricciones
      }
      return result
    #------------------------------------------------------------------------------------
    def getRestricciones(self):
      result=[]
      restriccionX={}


      for link in self.getLinks():
        if(link['source'] in restriccionX):
          restriccionX[link['source']].append(link['target'])
        else:
          restriccionX[link['source']]=[link['target']]

        if(link['target'] in restriccionX):
          restriccionX[link['target']].append(link['source'])
        else:
          restriccionX[link['target']]=[link['source']]

      for k,v in restriccionX.items():
        if(len(v)>=2):
          newRestriction={
              "type":"alignment",
              "axis":"x",
              "offsets":[]
          }
          for nodo in v:
            newRestriction["offsets"].append({"node":nodo,"offset":"0"})
          result.append(newRestriction)
      return result
    #------------------------------------------------------------------------------------
    def getLinks(self):
      result=[]
      for seq in self.leafNodes:
        if(len(seq.seq))>=2:
          #consigue el tweet mas valioso de
          topTweetId=seq.graphNodes[-1]['rawText'][0]
          #almacena los tokens
          topTweet=self.tokens.data['tokens'][int(topTweetId)].split()

          tempo={}
          #recorre la secuencia y ordena las palabras en el orden que aparecen
          for nodo in seq.graphLinks:
            tempo[nodo]=topTweet.index(nodo) % len(seq.graphLinks)
          tempo={k: v for k, v in sorted(tempo.items(), key=lambda item: item[1])}  

          #print(tempo)
          #print(seq.graphLinks)
          #genera los enlaces con las palabras seguidas
          for palabra in range(1,len(seq.seq)):
            source=list(tempo.keys())[palabra-1]
            source=seq.graphLinks[source]

            target=list(tempo.keys())[palabra]
            target=seq.graphLinks[target]
            
            result.append(
              {
                "source":source,
                "target":target,
                "strenght":0.3
              }
            )
      #print(json.dumps(result))
      return result
    #------------------------------------------------------------------------------------
    def getNodes(self):
      nodosDict=[]
      result=[]
      for seq in self.leafNodes:
        if(len(seq.seq))>=1:
          for nodo in seq.graphNodes:
            if nodo['name'] not in nodosDict:
              result.append(nodo)
              nodosDict.append(nodo['name'])
            else:
              continue
      return result
    #------------------------------------------------------------------------------------
    def plotTree(self):
        DotExporter(self.nodoRaiz).to_picture("ArbolSententree.png")
