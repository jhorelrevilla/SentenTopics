import pandas as pd

class Tokenizer:
    def __init__(self, df):
        #Se crea una lista con todas las palabras unicas
        self.tokenList = self.__getItemset(df)
        #Tokeniza los tweets filtrados y crea una columna de tokens
        df['tokens'] = df['tweetFiltrado'].apply(
            lambda x: self.__tokenizeTweet(str(x)))

    def __getItemset(self, BD):
        result = []
        for tweet in BD['tweetFiltrado'].values.tolist():
            for word in tweet.split():
                if (word in result):
                    continue
                else:
                    result.append(word)
        return result

    def __tokenizeTweet(self, tweet):
        result = []
        for word in tweet.split():
            result.append(str(self.tokenList.index(word)))
        return ' '.join(result)

    def tokenizeTopic(self,topic):
        result = []
        for word in topic:
            if(word not in self.tokenList):
                continue
            result.append(str(self.tokenList.index(word)))
        return result

    def token2word(self,token)->str:
        if token<0 or token>len(self.tokenList):
            return ""
        return str(self.tokenList[token])
    
    def word2token(self,word)->int:
        if word not in self.tokenList:
            return -1
        return int(self.tokenList.index(word))