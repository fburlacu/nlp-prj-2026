
from collections import Counter
import numpy as np
import scipy.sparse as sp
from data.preprocessing import tokenize

class BM25:
    def __init__(self, texts, k1=1.2, b=0.75):
        toks = [tokenize(t) for t in texts]
        self.vocab, rows, cols, vals = {}, [], [], []
        for d, ts in enumerate(toks):
            for t, c in Counter(ts).items():
                rows.append(d); cols.append(self.vocab.setdefault(t, len(self.vocab)))
                vals.append(c)
        tf = sp.coo_matrix((vals, (rows, cols)), shape=(len(toks), len(self.vocab)), dtype=np.float32)
        dl = np.bincount(tf.row, weights=tf.data, minlength=len(toks))
        avgdl = dl.mean()
        df = np.bincount(tf.col, minlength=len(self.vocab))
        N = len(toks)
        idf = np.log1p((N - df + 0.5) / (df + 0.5))           # Lucene idf
        w = tf.data * (k1 + 1) / (tf.data + k1 * (1 - b + b * dl[tf.row] / avgdl)) * idf[tf.col]
        self.W = sp.csc_matrix((w, (tf.row, tf.col)), shape=tf.shape)   # passages x terms

    def scores(self, query):
        ids = [self.vocab[t] for t in tokenize(query) if t in self.vocab]
        if not ids:
            return np.zeros(self.W.shape[0], np.float32)
        return np.asarray(self.W[:, ids].sum(axis=1)).ravel()
