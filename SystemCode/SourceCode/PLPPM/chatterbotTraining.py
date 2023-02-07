from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot import filters
from chatterbot.comparisons import JaccardSimilarity
import logging
'''
This is an example showing how to create an export file from
an existing chat bot that can then be used to train other bots.
'''
logging.basicConfig(level=logging.DEBUG)

chatbot = ChatBot( 'PLPPM',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    filters=[filters.get_recent_repeated_responses],
    statement_comparison_function=JaccardSimilarity,
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


# First, lets train our bot with some data
trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train('./chatbot_intent/')

# Now we can export the data to a file
trainer.export_for_training('./training_data.json')