import numpy as np
from numpy.linalg import norm
'''
Short Text Topic Modeling via SeaNMF
'''


class SeaNMFL1(object):
    def __init__(
            self,
            A, S,
            IW1=[], IW2=[], IH=[],
            alpha=1.0, beta=0.1, n_topic=10, max_iter=100, max_err=1e-3,
            rand_init=True, fix_seed=False):
        '''
        0.5*||A-WH^T||_F^2+0.5*alpha*||S-WW_c^T||_F^2+0.5*beta*||W||_1^2
        W = W1
        Wc = W2
        '''
        if fix_seed:
            np.random.seed(0)

        self.A = A
        self.S = S

        self.n_row = A.shape[0]
        self.n_col = A.shape[1]

        self.n_topic = n_topic
        self.max_iter = max_iter
        self.alpha = alpha
        self.beta = beta
        self.B = np.ones([self.n_topic, 1])
        self.max_err = max_err

        if rand_init:
            self.nmf_init_rand()
        else:
            self.nmf_init(IW1, IW2, IH)
        self.nmf_iter()

    def nmf_init_rand(self):
        self.W1 = np.random.random((self.n_row, self.n_topic))
        self.W2 = np.random.random((self.n_row, self.n_topic))
        self.H = np.random.random((self.n_col, self.n_topic))

        for k in range(self.n_topic):
            self.W1[:, k] /= norm(self.W1[:, k])
            self.W2[:, k] /= norm(self.W2[:, k])

    def nmf_init(self, IW1, IW2, IH):
        self.W1 = IW1
        self.W2 = IW2
        self.H = IH

        for k in range(self.n_topic):
            self.W1[:, k] /= norm(self.W1[:, k])
            self.W2[:, k] /= norm(self.W2[:, k])

    def nmf_iter(self):
        loss_old = 1e20
        for i in range(self.max_iter):
            self.nmf_solver()
            loss = self.nmf_loss()
            if loss_old-loss < self.max_err:
                break
            loss_old = loss

    def nmf_solver(self):
        '''
        using BCD framework
        '''
        epss = 1e-20
        # Update W1
        AH = np.dot(self.A, self.H)
        SW2 = np.dot(self.S, self.W2)
        HtH = np.dot(self.H.T, self.H)
        W2tW2 = np.dot(self.W2.T, self.W2)
        W11 = self.W1.dot(self.B)

        for k in range(self.n_topic):
            num0 = HtH[k, k]*self.W1[:, k] + \
                self.alpha*W2tW2[k, k]*self.W1[:, k]
            num1 = AH[:, k] + self.alpha*SW2[:, k]
            num2 = np.dot(self.W1, HtH[:, k]) + self.alpha * \
                np.dot(self.W1, W2tW2[:, k]) + self.beta*W11[0]
            self.W1[:, k] = num0 + num1 - num2
            self.W1[:, k] = np.maximum(self.W1[:, k], epss)  # project > 0
            self.W1[:, k] /= norm(self.W1[:, k]) + epss  # normalize
        # Update W2
        W1tW1 = self.W1.T.dot(self.W1)
        StW1 = np.dot(self.S, self.W1)
        for k in range(self.n_topic):
            self.W2[:, k] = self.W2[:, k] + \
                StW1[:, k] - np.dot(self.W2, W1tW1[:, k])
            self.W2[:, k] = np.maximum(self.W2[:, k], epss)
        # Update H
        AtW1 = np.dot(self.A.T, self.W1)
        for k in range(self.n_topic):
            self.H[:, k] = self.H[:, k] + AtW1[:, k] - \
                np.dot(self.H, W1tW1[:, k])
            self.H[:, k] = np.maximum(self.H[:, k], epss)

    def nmf_loss(self):
        '''
        Calculate loss
        '''
        loss = norm(self.A - np.dot(self.W1,
                    np.transpose(self.H)), 'fro')**2/2.0
        if self.alpha > 0:
            loss += self.alpha * \
                norm(np.dot(self.W1, np.transpose(self.W2))-self.S, 'fro')**2/2.0
        if self.beta > 0:
            loss += self.beta*norm(self.W1, 1)**2/2.0

        return loss

    def get_lowrank_matrix(self):
        return self.W1, self.W2, self.H

    def save(self, W1file='W.txt'):
        np.savetxt(W1file, self.W1)
# ---------------------------------------


def calculate_PMI(AA, topKeywordsIndex):
    '''
    Reference:
    Short and Sparse Text Topic Modeling via Self-Aggregation
    '''
    D1 = np.sum(AA)
    n_tp = len(topKeywordsIndex)
    PMI = []
    for index1 in topKeywordsIndex:
        for index2 in topKeywordsIndex:
            if index2 < index1:
                if AA[index1, index2] == 0:
                    PMI.append(0.0)
                else:
                    C1 = np.sum(AA[index1])
                    C2 = np.sum(AA[index2])
                    PMI.append(np.log(AA[index1, index2]*D1/C1/C2))
    avg_PMI = 2.0*np.sum(PMI)/float(n_tp)/(float(n_tp)-1.0)

    return avg_PMI
# ---------------------------------------


def crearMatrizDocTerm(data, vocab_min_count, vocab_max_size):
    vocab = {}
    for line in data:
        for wd in line.split():
            try:
                vocab[wd] += 1
            except:
                vocab[wd] = 1

    vocab_arr = [[wd, vocab[wd]]
                 for wd in vocab if vocab[wd] > vocab_min_count]
    vocab_arr = sorted(vocab_arr, key=lambda k: k[1])[::-1]
    vocab_arr = vocab_arr[:vocab_max_size]
    vocab_arr = sorted(vocab_arr)

    vocab = vocab_arr
    vocab2id = {itm[1][0]: itm[0] for itm in enumerate(vocab_arr)}
    # --------------- CALCULAR matriz documento terminos
    data_arr = []
    for line in data:
        arr = line.split()
        arr = [int(vocab2id[wd]) for wd in arr if wd in vocab2id]
        data_arr.append(arr)

    docs = data_arr
    n_docs = len(docs)
    n_terms = len(vocab)
    del vocab2id
    # ----------------------------------------------------------------------
    # --------------- CALCULAR matrix co ocurrencia
    dt_mat = np.zeros([n_terms, n_terms])
    for itm in docs:
        for kk in itm:
            for jj in itm:
                dt_mat[int(kk), int(jj)] += 1.0

    # --------------- CALCULAR PPMI
    D1 = np.sum(dt_mat)
    SS = D1*dt_mat
    for k in range(n_terms):
        SS[k] /= np.sum(dt_mat[k])
    for k in range(n_terms):
        SS[:, k] /= np.sum(dt_mat[:, k])

    dt_mat = []
    SS[SS == 0] = 1.0
    SS = np.log(SS)
    SS[SS < 0.0] = 0.0

    # --------------- CALCULAR term doc matrix

    dt_mat = np.zeros([n_terms, n_docs])
    for k in range(n_docs):
        for j in docs[k]:
            dt_mat[int(j), int(k)] += 1.0

    return vocab, dt_mat, SS
# ---------------------------------------


def extractTopics(data, n_topic):
    data = data['tweetFiltrado'].to_list()
    vocab_max_size = 2500
    vocab_min_count = 30
    n_topKeyword = 30
    vocab, dt_mat, SS = crearMatrizDocTerm(
        data, vocab_min_count, vocab_max_size)
    model = SeaNMFL1(dt_mat, SS, n_topic=n_topic)

    W = model.W1
    PMI_arr = []
    n_topKeyword = 10
    for k in range(n_topic):
        topKeywordsIndex = W[:, k].argsort()[::-1][:n_topKeyword]
        PMI_arr.append(calculate_PMI(dt_mat, topKeywordsIndex))
    index = np.argsort(PMI_arr)

    topics = []
    for k in index:
        topic = []
        for w in np.argsort(W[:, k])[::-1][:n_topKeyword]:
            topic.append(vocab[w][0])
        topics.append(topic)
    return topics
