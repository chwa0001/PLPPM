import tensorflow as tf
from tensorflow import keras
import spacy
import pickle
import numpy as np
from transformers import AutoTokenizer, AutoModel, pipeline
from neo4j import GraphDatabase

class GQLGenerator(object):
    def __init__(self, path) -> None:
        self.nlp = spacy.load("en_core_web_sm")
        with tf.device('/CPU:0'):
            self.gql_model = keras.models.load_model(f"{path}/gql/model/gqlmodel.h5")
        with open(f'{path}/gql/model/enc_class.pkl','rb') as f:
            self.enc_class = pickle.load(f)
        model = AutoModel.from_pretrained('bert-base-uncased')
        tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.fe = pipeline('feature-extraction', model=model, tokenizer=tokenizer)
        self.graph = GraphDatabase.driver(
            "neo4j://localhost:7687",
            auth=("neo4j", "password")
        )
        pass

    def translate_to_gql(self,text):

        if text.startswith('In w'):
            text = text[3].upper() + text[4:]

        ques_ent = self.nlp(text)
        if len(ques_ent.ents)>0:
            ent_pred = ques_ent.ents[0].text
        else:
            ent_pred = ''

        maxlen = [50,768]
        input_vec = np.zeros([1,maxlen[0],maxlen[1]])
        features = self.fe([text])
        features = np.squeeze(features)
        input_vec[0,0:features.shape[0],:] = features
        with tf.device('/CPU:0'):
            y_prediction = self.gql_model.predict(input_vec)
        y_prediction = np.argmax(y_prediction, axis = 1)
        rel_pred = self.enc_class.classes_[y_prediction[0]]

        query = (
        "MATCH (n1:Entity {name: $ent1})-[rel:"+rel_pred.replace(" ","_")+"] -> (n2:Entity) "
        "RETURN n1, n2, rel"
        )

        answer = None
        with self.graph.session() as session:
            results = session.run(query, ent1=ent_pred)
            for result in results:
                answer = result['n2']['name']
        
        #Rule based for text generation
        start = 0
        rule = ''
        sentList = []
        tempKey = ''
        tempList = []
        for sent in ques_ent.sents:
            for token in sent:

                #rule 1
                if not start and token.text=='Who':
                    start = 1
                    rule = token.text
                elif rule=='Who':
                    if start==1 and (token.pos_ == 'AUX') and len(tempList)==0 and token.text in ['is','are','was','were','has','have']:
                        start = 2
                        tempKey = f"{answer} {token.text}"
                        sentList.append(tempKey)
                    elif start==1 and (token.pos_ == 'VERB') and len(tempList)==0 :
                        start = 2
                        tempKey = f"{answer} {token.text}"
                        sentList.append(tempKey)
                    elif start==1 and tempKey=='' and (token.pos_ == 'PROPN' or token.pos_ == 'CCONJ' or token.pos_ == 'NOUN' or token.pos_ == 'VERB'):
                        tempList.append(token.text)
                    elif start==1 and len(tempList) and ((token.pos_ == 'ADP' and token.head.pos_=='VERB') or (token.pos_ == 'ADV' and token.head.pos_=='VERB') or token.head.pos_!='VERB'):
                        if token.head.pos_=='VERB':
                            tempList.append(f"{token.text} {answer}")
                        else:
                            tempList.append(f"{answer} {token.text}")
                        start = 2
                        sentList.extend(tempList)
                    elif start==2 and not token.is_sent_end:
                        sentList.append(token.text)

                #rule 2
                elif not start and token.text=='When':
                    start = 1
                    rule = token.text
                elif rule=='When':
                    if start==1 and (token.pos_ == 'AUX') and token.text in ['is','are','was','were','did','will']:
                        start = 2
                        if token.text in ['was','were','is','are']:
                            tempKey = token.text
                    elif start==2 and tempKey!='' and not token.is_sent_end and not token.is_punct and token.pos_ == 'VERB' and token.dep_=='ROOT':
                        sentList.append(f"{tempKey} {token.text}")
                        tempKey = ''
                    elif start==2 and not token.is_sent_end:
                        sentList.append(token.text)
                    elif token.is_sent_end and token.is_punct:
                        sentList.append(f"in {answer}")

                #rule 3
                elif not start and (token.text=='What' or token.text=='Which'):
                    start = 1
                    rule = token.text
                elif rule=='What' or rule=='Which':
                    if start==1 and (token.pos_ == 'NOUN') and len(tempList)==0:
                        continue
                    elif start==1 and (token.pos_ == 'AUX') and len(tempList)==0 and token.text in ['did','does','do']:
                        continue
                    elif start==1 and tempKey=='' and len(tempList)==0 and (token.pos_ == 'AUX') and token.text in ['is','are','was','were','will']:
                        start = 2
                        tempKey = f"{answer} {token.text}"
                        sentList.append(tempKey)
                    elif start==1 and tempKey=='' and (token.pos_ == 'VERB') and len(tempList)==0:
                        start = 2
                        tempKey = f"{answer} {token.text}"
                        sentList.append(tempKey)
                    elif start==1 and tempKey=='' and ( token.pos_ == 'AUX' or token.pos_ == 'PROPN' or token.pos_ == 'CCONJ' or token.pos_ == 'NOUN' or token.pos_ == 'VERB'):
                        tempList.append(token.text)
                    elif start==1 and len(tempList) and ((token.pos_ == 'ADP' and token.head.pos_=='VERB') or (token.pos_ == 'ADV' and token.head.pos_=='VERB') or token.head.pos_!='VERB'):
                        if token.head.pos_=='VERB':
                            tempList.append(f"{token.text} {answer}")
                        else:
                            tempList.append(f"{answer} {token.text}")
                        start = 2
                        sentList.extend(tempList)
                    elif start==2 and not token.is_sent_end:
                        sentList.append(token.text)

                #rule 4
                elif not start and token.text=='Where':
                    start = 1
                    rule = token.text
                elif rule=='Where':
                    if start==1 and (token.pos_ == 'AUX') and token.text in ['is','are','was','were','did','will']:
                        start = 2
                    if token.text in ['was','were','is','are']:
                        tempKey = token.text
                    elif start==2 and tempKey!='' and not token.is_sent_end and not token.is_punct and token.pos_ == 'VERB' and token.dep_=='ROOT':
                        sentList.append(f"{tempKey} {token.text}")
                        tempKey = ''
                    elif start==2 and not token.is_sent_end:
                        sentList.append(token.text)
                    elif token.is_sent_end and token.is_punct:
                        sentList.append(f"in {answer}")

        if len(sentList)!=0 and answer:
            reply = ' '.join(sentList)
            reply = f"{reply[0].upper()}{reply[1:]}." if answer in reply else answer
        else:
            reply = answer
        return (query,reply)