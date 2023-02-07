import pickle

class intentClassification(object):

    def __init__(self,path) -> None:
        with open(f'{path}/intention/model/bigram_vectorizer.pkl','rb') as f:
            self.bigram_vectorizer = pickle.load(f)

        with open(f'{path}/intention/model/ch21.pkl','rb') as f:
            self.ch21 = pickle.load(f)

        with open(f'{path}/intention/model/clr_svm.pkl','rb') as f:
            self.clr_svm = pickle.load(f)
    
    def predict(self,queryText) -> dict:
        query_bigram_vectors = self.bigram_vectorizer.transform([queryText])
        query_bigram_Kbest = self.ch21.transform(query_bigram_vectors)
        prediction = self.clr_svm.predict(query_bigram_Kbest)[0]
        predictedClass = {'sql':0,'gql':0,'terms':0,'casual':0}
        predictedClass[prediction] = 1
        return predictedClass



