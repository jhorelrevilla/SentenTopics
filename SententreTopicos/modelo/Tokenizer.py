class Tokenizer:
    def __init__(self, df):
        # diccionario de todos los tokens unicos
        self.itemset = self.getItemset(df)
        self.data = df[['tweet', 'tweetFiltrado', 'likes_count']].copy()
        # convierte el tweet en una serie de tokens
        self.data['tokens'] = self.data['tweetFiltrado'].apply(
            lambda x: self.tokenizeTweet(str(x), self.itemset))

    def getItemset(self, BD):
        result = {}
        contador = 0
        for tweet in BD['tweetFiltrado'].values.tolist():
            for word in tweet.split():
                if (word in result):
                    continue
                else:
                    result[word] = contador
                    contador += 1
        return result

    def tokenizeTweet(self, tweet, tokenDict):
        result = []
        for word in tweet.split():
            result.append(str(tokenDict[word]))
        return ' '.join(result)