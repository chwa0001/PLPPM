from django.shortcuts import render

from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response

from .apps import BackendConfig
from .models import *
import datetime
# Create your views here.

def TextToSQLQuery(conversation,query):
    error = None
    try:
        sqlquery,generatedText = BackendConfig.sql.translate_to_sql(f"translate to SQL: {query}")
    except Exception as e:
        error = str(e)
        sqlquery = None
        generatedText = 'Sorry I cannot find the information from the SPI dataset'
    replyData = {
                    "text": generatedText,
                    "search_text": "",
                    "conversation": f"{conversation}",
                    "persona": "bot:PLPPM",
                    "tags": ['sql'],
                    "in_response_to": query,
                    "search_in_response_to": "",
                    "created_at": str(datetime.datetime.now()),
                    "sql_query":sqlquery,
                    "error": error
                }
    return replyData

def TextToGQLQuery(conversation,query):
    error = None
    try:
        gqlquery,answer = BackendConfig.gql.translate_to_gql(query)
        if answer:
            generatedText = answer
        else:
            generatedText = 'Sorry I cannot find the information from the US Financial News Articles'
    except Exception as e:
        error = str(e)
        gqlquery = None
        generatedText = 'Sorry I cannot find the information from the US Financial News Articles'
    replyData = {
                    "text": generatedText,
                    "search_text": "",
                    "conversation": f"{conversation}",
                    "persona": "bot:PLPPM",
                    "tags": ['gql'],
                    "in_response_to": query,
                    "search_in_response_to": "",
                    "created_at": str(datetime.datetime.now()),
                    "gql_query":gqlquery,
                    "error": error
                }
    return replyData

def TextToTermDefinition(conversation,query):
    error = None
    try:
        corpusScore = BackendConfig.terms.predict(query)
        if len(corpusScore)>0:
            questionIndex = corpusScore[0][1]
            question = TermAndQuestion.objects.filter(questionID=questionIndex)
            if question.exists():
                generatedText = question[0].termID.definition
            else:
                raise Exception('Question ID cannot be retrieved in Term And Question table.')
        else:
            generatedText = 'Sorry I cannot find the information from the Investopedia Terms dataset'
    except Exception as e:
        error = str(e)
        corpusScore = []
        generatedText = 'Sorry I cannot find the information from the Investopedia Terms dataset'
    score = corpusScore[0][0] if len(corpusScore)>0 else None
    replyData = {
                    "text": generatedText,
                    "search_text": "",
                    "conversation": f"{conversation}",
                    "persona": "bot:PLPPM",
                    "tags": [],
                    "in_response_to": query,
                    "search_in_response_to": "",
                    "created_at": str(datetime.datetime.now()),
                    "score": score,
                    "error": error
                }
    return replyData

def chatterbotIntent(statement,conversation):
    try:
        reply = BackendConfig.bot.get_response(statement)
        replyData = reply.serialize()
        replyData['error'] = None
    except Exception as e:
        error = str(e)
        replyData = {
                    "text": 'I am sorry, but I do not understand.',
                    "search_text": "",
                    "conversation": f"{conversation}",
                    "persona": "bot:PLPPM",
                    "tags": [],
                    "in_response_to": statement.get('text'),
                    "search_in_response_to": "",
                    "created_at": str(datetime.datetime.now()),
                    "error": error
                }   
    return replyData

def index(request, *args, **kwargs):
    return render(request, 'ui/index.html')

class AskChatBot(APIView):
    def post(self, request, format=None):
        try:
            statement = request.data.get('data')
            submittedText = statement.get('text')
            intention = statement.get('intent')
            conversation = statement.get('conversation')
            if not intention:
                intentDetected = BackendConfig.intentClassifer.predict(submittedText)

                sqlIntent = intentDetected.pop('sql',0)
                gqlIntent = intentDetected.pop('gql',0)
                termsIntent = intentDetected.pop('terms',0)
                casualIntent = intentDetected.pop('casual',0)
            else:
                sqlIntent = intention == 'sql'
                gqlIntent = intention == 'gql'
                casualIntent = intention == 'casual'
                termsIntent = intention == 'terms'
                submittedText = statement.get('previous_request')

            if sqlIntent and not gqlIntent and not termsIntent and not casualIntent:
                replyData = TextToSQLQuery(conversation,submittedText)
            elif gqlIntent and not sqlIntent and not termsIntent and not casualIntent:
                replyData = TextToGQLQuery(conversation,submittedText)
            elif termsIntent and not gqlIntent and not sqlIntent and not casualIntent:
                replyData = TextToTermDefinition(conversation,submittedText)
            elif casualIntent and not termsIntent and not sqlIntent and not gqlIntent:
                statement['text'] = submittedText
                conversation = statement.get('conversation')
                replyData = chatterbotIntent(statement,conversation)
            else:
                raise Exception('incorrect intent dectected')
            return Response(replyData, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'Bad Request': str(e)}, status=status.HTTP_400_BAD_REQUEST)