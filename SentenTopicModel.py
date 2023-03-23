"""
El nodo principal deberia ser un Sententree de todos los datos?



-Cada Nodo debe formar un Sententree
-El tamanio de las palabras

"""
import pandas as pd
from modelo.SententreeModel import Sententree
from modelo.Tokenizer import Tokenizer
from modelo.seanmfTopic import extractTopics
from anytree import Node,PreOrderIter,search
import json


class Sententopic:
    def __init__(self, dataDf, numPalabrasPerTopic):
        #verificar que tenga la estructura necesaria
        dataDf=dataDf[['tweet', 'tweetFiltrado', 'likes_count']].copy()
        self.numPalabrasPerTopic = numPalabrasPerTopic
        self.numeroTotalTweets=dataDf.shape[0]
        self.numeroTopicos=0
        self.tokens=Tokenizer(dataDf)
        
        self.root=Node(
            "-1",
            sententree=False,
            visible=False
        )
        self.crearSententreePerTopics(
            data=dataDf,
            numTopics=10,
            parent=self.root 
        )        
        # self.getDataJson2()
    #-------------------------------------------------------
    def crearSententreePerTopics(self, data, numTopics, parent):
        # Extraer topicos
        topicList = extractTopics(
            data=data['tweetFiltrado'].to_list(), 
            numTopics=numTopics
            )
        # Dividir data por los topicos 
        dataClasificada = self.clasificarData(
            data=data, 
            topicList=topicList
            )
        # Tokenizar el topico
        topicList=[[self.tokens.word2token(word) for word in topic] for topic in topicList]
        # Crear Sententree por cada topico
        for i in range(len(dataClasificada)):
            
            # print(f"creando Sententree con {dataClasificada[i].shape[0]}")
            
            self.numeroTopicos+=1

            sententree=Sententree(
                    data=dataClasificada[i],
                    palabrasNecesarias=self.numPalabrasPerTopic,
                    topic=topicList[i],
                    numTopic=self.numeroTopicos,
                    numTotalDf=data.shape[0],
                    tokens=self.tokens
                )
            Node(
                f"{self.numeroTopicos}",
                parent=parent,
                visible=False,
                sententree=sententree,         
            )            
    #-------------------------------------------------------
    def clasificarTweet(self, tweet, topicList):
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
    #-------------------------------------------------------
    def clasificarData(self, data, topicList):
        data['topico'] = data.apply(
            lambda x: self.clasificarTweet(
                tweet=x.tweetFiltrado,
                topicList=topicList
            ), axis=1)

        result = []
        for topic in range(len(topicList)):
            topicDf = data.loc[data['topico'] == topic]
            #print(f"topico {topic} tienen {topicDf.shape}")
            topicDf.reset_index(drop=True, inplace=True)
            result.append(topicDf.copy())
        return result
    #------ OPERACIONES
    def activarNodos(self,nodos:list):
        escogidos=search.findall(self.root, filter_=lambda node: node.name in nodos)
        for nodo in escogidos:
            nodo.visible=True
    #-------------------------------------------------------
    def expandirNodo(self, nodos:list,numero_topicos:int):
        # Recorrer todos los nodos escogidos
        # print(f"Buscar Topicos {nodos}")
        escogidos=search.findall(self.root, filter_=lambda node: node.name in nodos)
        # parent_node.children.remove(node)
        for node in escogidos:
            df=node.sententree.data.copy()
            if (df.shape[0] <= 50):
                continue
            self.crearSententreePerTopics(
                data=df,
                numTopics=numero_topicos,
                parent=node
                )
        return
    # -------------------------------------------------------
    def eliminarNodo(self,nodos:list):
        print(f"Borrar los nodos {nodos}")
        escogidos=search.findall(self.root, filter_=lambda node: node.name in nodos)
        # parent_node.children.remove(node)
        for node in escogidos:
            # node.parent.children.remove(node)
            
            children_list=list(node.parent.children)
            # print(f"Lista de hijos {children_list}")
            children_list=filter(lambda x:x.name!=node.name,children_list)
            # print(f"Nueva lista de hijos {children_list}")
            node.parent.children=tuple(children_list)
    #-------------------------------------------------------
    def mezclarTopicos(self, nodos:list):
        nodos_escogidos=search.findall(self.root, filter_=lambda node: node.name in nodos)
        nodos=[nodo.name for nodo in nodos_escogidos]
        
        nodo_menor=nodos_escogidos[0]

        merged_df=[]
        merged_topics=[]

        for nodo in nodos_escogidos:
            merged_df.append(nodo.sententree.data)
            merged_topics+=nodo.sententree.topic
            if len(nodo.path) < len(nodo_menor.path):
                nodo_menor=nodo
        
        print("*" * 10)
        print(nodo_menor.children)
        nodo_menor_index=nodos_escogidos.index(nodo_menor)
        nodos.pop(nodo_menor_index)
        self.eliminarNodo(nodos)

        print(nodo_menor.children)

        merged_df = pd.concat(merged_df)
        merged_df.reset_index(drop=True, inplace=True)
        merged_df.sort_values(by=['likes_count'], ascending=False)

        merged_topics=list(dict.fromkeys(merged_topics))

    

        new_sententree=Sententree(
                data=merged_df,
                palabrasNecesarias=self.numPalabrasPerTopic,
                topic=merged_topics,
                numTopic=self.numeroTopicos,
                numTotalDf=merged_df.shape[0],# Aca debe ir el tamanio del padre
                tokens=self.tokens
            )
        
        nodo_menor.sententree=new_sententree


        # new_node=Node(
        #     f"{self.numeroTopicos}",
        #     parent=nodo_menor.parent,
        #     visible=False,
        #     sententree=new_sententree,
        # )

        # for child in nodo_menor.children:
        #     child.parent=new_node
    #-------------------------------------------------------
    def getNodeData(self,node):
        if not node.parent:
            return [{
                    "name": "root",
                    "label": " ",
                    "width": 60,
                    "heigth": 40
                   }]
        return node.sententree.getNodes(node.visible)
    #-------------------------------------------------------
    def getDataJson2(self):
        nodosID = []
        nodos = []
        links = []
        restricciones = []
        grupos = []

        # Recorre el arbol para obtener todos los nodos,links,restricciones y grupos
        for node in PreOrderIter(self.root):
            nodoJson=self.getNodeData(node)

            if not node.parent:
                nodos.extend(nodoJson)
                nodosID.append(nodoJson[0]['name'])
                continue

            # Reemplazar label de los nodos 
            for nodo in nodoJson:
                nodosID.append(nodo['name'])
                # nodo['label']=str(self.tokens.token2word(int(nodo['label'])))

            nodos.extend(nodoJson)
            # Links y restricciones del Sententopic
            links.append(
                {
                    "source": self.getNodeData(node.parent)[0]['name'],
                    "target": nodoJson[0]['name'],
                    "length": 0,
                    "tipo":"sententopic"
                }                
            )
            restricciones.append(
                {
                    "axis": "x",
                    "left": self.getNodeData(node.parent)[0]['name'],
                    "right": nodoJson[0]['name'],
                    "tipo": "sententopic",
                    "gap":300
                }
            )

            links.extend(node.sententree.getLinks(node.visible))
            restricciones.extend(node.sententree.getRestricciones(node.visible))
            grupos.extend(node.sententree.getGrupos(node.visible))

        # Actualiza los links,restricciones y grupos

        # Links
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
        
        # Restricciones
        for restriccion in restricciones:
            if('offset' in restriccion.keys()):
                for offset in restriccion['offsets']:
                    offset['node'] = nodosID.index(offset['node'])
            
            restriccion['axis'] = "x"
            restriccion['left'] = nodosID.index(restriccion['left'])
            restriccion['right'] = nodosID.index(restriccion['right'])
            restriccion['gap']=150
        
        # Grupos
        for grupo in grupos:
            newNodes=[]
            for nodo in grupo['leaves']:
                newNodes.append(nodosID.index(nodo))
            grupo['leaves']=newNodes
            grupo['padding']=5
            #grupo['leaves'] = [nodosID.index(nodo) for nodo in grupo['leaves']]

        return {
            "nodes": nodos,
            "links": links,
            "constraints": restricciones,
            "groups": grupos
        }
    #-------------------------------------------------------
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
        """
        Se necesita utilizar las posiciones de los nodos para los
        Links, restricciones y grupos 
        """
        
        for sententree in self.SententreeList:
            if not sententree.visible:
                #print(f"nodo no visible: {sententree.numTopic}")
                continue
            nodos.extend(sententree.getNodes())
            links.extend(sententree.getLinks())
            restricciones.extend(sententree.getRestricciones())
            grupos.extend(sententree.getGrupos())

        for nodo in nodos:
            nodosID.append(nodo['name'])

        #print(nodosID)

        # LINKS Y RESTRICCIONES DEL SENTENTOPIC
        sententopicLinks=[]
        SententopicRestricciones=[]
        for sententree in self.SententreeList:
            #print(f"enlaces para {sententree.name}")

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
