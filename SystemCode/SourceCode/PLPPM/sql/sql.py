from torch import cuda
from transformers import AutoTokenizer, T5ForConditionalGeneration
import sqlite3
import spacy

class SQLGenerator(object):
    def __init__(self, path) -> None:
        self.nlp = spacy.load("en_core_web_sm")
        self.device = 'cuda' if cuda.is_available() else 'cpu'
        model_path = f'{path}/sql/model/checkpoint-5625'
        tokenizer_path = f'{path}/sql/tokenizer'
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.dbCon = sqlite3.connect(f'{path}/spi_index_labelled vFinal.db', check_same_thread=False)
        pass

    def getDataFromDB(self,sqlquery):
        cursor = self.dbCon.cursor()
        response = cursor.execute(sqlquery)
        return response.fetchall()

    def translate_to_sql(self,text):
        inputs = self.tokenizer(text, padding='longest', max_length=64, return_tensors='pt')
        input_ids = inputs.input_ids
        attention_mask = inputs.attention_mask
        output = self.model.generate(input_ids, attention_mask=attention_mask, max_length=64)
        sqlquery = self.tokenizer.decode(output[0], skip_special_tokens=True)

        #retrieve data from db
        sqlData = self.getDataFromDB(sqlquery)
        reply = ''
        if len(sqlData)>0:
            answer = ', '.join([str(data[0]) for data in sqlData if len(data)>0])
            ques_ent = self.nlp(text)
            start = 0
            sentList = []
            #rule 1
            for sent in ques_ent.sents:
                for token in sent:
                    if not start and (token.pos_ == 'PRON' and token.head.pos_ == 'AUX'):
                        start = 1
                    elif start==1 and (token.pos_ == 'AUX'):
                        start = 2
                    elif start==2 and not token.is_sent_end and not token.is_punct:
                        sentList.append(token.text)
            if len(sentList)==0:
                #rule 2
                start = 0
                for sent in ques_ent.sents:
                    for token in sent:
                        if not start and (token.pos_ == 'VERB' and token.dep_ == 'ROOT'):
                            start = 1
                        elif start==1 and (token.pos_ == 'DET' or token.pos_ == 'PRON'):
                            start = 2
                            if token.pos_ == 'DET':
                                sentList.append(token.text)
                        elif start==2 and not token.is_sent_end and not token.is_punct:
                            sentList.append(token.text)
                if len(sentList)==0:
                    start = 0
                    #rule 3
                    for sent in ques_ent.sents:
                        for token in sent:
                            if token.pos_ == 'NOUN':
                                start = 1
                            break
                        break
                    if start:
                        if ques_ent.doc[-1].is_punct:
                            reply = f"{ques_ent.doc[:-1].text}: {answer}"
                        else:
                            reply = f"{ques_ent.doc.text }: {answer}"
                    else:
                        #rule 4
                        entities = ques_ent.ents
                        if len(entities)>0:
                            length = len(entities[0])
                            if entities[0].text==ques_ent[:length].text:
                                if ques_ent.doc[-1].is_punct:
                                    reply = f"{ques_ent.doc[:-1].text}: {answer}"
                                else:
                                    reply = f"{ques_ent.doc.text}: {answer}"
                            else:
                                reply = answer
                        else:
                            reply = answer
                else:
                    reply = f"{' '.join(sentList)}: {answer}"
            else:
                reply = f"{' '.join(sentList)}: {answer}"
        else:
            reply = 'Sorry I cannot find the information from the SPI dataset'

        
        return (sqlquery, reply)
    
    

