import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import util
import torch
import numpy as np

class terms(object):

    def __init__(self,path) -> None:
        with open(f'{path}/investopedia/model/SBert_embedder.pkl','rb') as f:
            self.SBert_embedder = pickle.load(f)

        with open(f'{path}/investopedia/model/corpus_embeddings.pkl', 'rb') as f:
            self.corpus_embeddings = pickle.load(f)

        with open(f'{path}/investopedia/model/tfidf_matrix.pkl', 'rb') as f:
            self.tfidf_matrix = pickle.load(f)

        with open(f'{path}/investopedia/model/tfidf.pkl','rb') as f:
            self.tfidf = pickle.load(f)

    def predict(self, query,k_coeff=0.5, threshold=0.92):
        query_vector = self.tfidf.transform([query.lower()])
        cosine_sim = cosine_similarity(self.tfidf_matrix, query_vector)
        tfidf_score = torch.FloatTensor(np.transpose(cosine_sim)[0])

        query_embedding = self.SBert_embedder.encode([query], convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0].cpu()

        final_scores = k_coeff*cos_scores + (1-k_coeff)*tfidf_score
        scores,indices = torch.topk(final_scores, k=5)
        return [ (float(scores[index].item()),int(corpusIndex.item())) for index, corpusIndex in enumerate(indices) if float(scores[index].item())>threshold ]