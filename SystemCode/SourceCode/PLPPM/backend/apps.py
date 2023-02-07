from django.apps import AppConfig
from chatterbot.chatterbot import ChatBot
from chatterbot import filters
from chatterbot.comparisons import JaccardSimilarity
import logging
from intention.intentClassification import intentClassification
from investopedia.terms import terms
from chatterbot.response_selection import get_random_response
from sql.sql import SQLGenerator
from gql.gql import GQLGenerator

import os

class BackendConfig(AppConfig):
    name = 'backend'

    currentProjectPath = os.getcwd()
    intentClassifer = intentClassification(currentProjectPath)
    terms = terms(currentProjectPath)
    sql = SQLGenerator(currentProjectPath)
    gql = GQLGenerator(currentProjectPath)

    logging.basicConfig(level=logging.DEBUG)
    bot = ChatBot( 'PLPPM',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    filters=[filters.get_recent_repeated_responses],
    statement_comparison_function=JaccardSimilarity,
    response_selection_method=get_random_response,
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ],
    read_only=True,
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.85
        }
    ],
    database_uri='sqlite:///chatterbot.sqlite3')
