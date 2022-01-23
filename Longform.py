
# create class for managing creation of longform documents


from pydantic import NoneBytes
from streamlit import echo
import app.utilities.csd_reduced_fx as csd
import app.utilities.gpt3_reduced_fx
import app.utilities.syntheticdata
from gpt3_reduced_fx import presets_parser, gpt3complete
import uuid
from uuid import uuid4
import os
from os import environ as osenv
import stripe
#import createsyntheticdata as csd

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "price_id": os.environ["STRIPE_PRICE_ID"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"],
}

stripe.api_key = stripe_keys["secret_key"]

import openai

openai.api_key = os.environ['OPENAI_API_KEY']
openai_user_id_for_safety_tracking = os.environ['OPENAI_USER_ID_FOR_SAFETY_TRACKING']


tuple1 = ['SimpleXmasStoryIdeas', 'csd', ['n=3'],'intelligent tanks', None, NoneBytes]
tuple2 = ['SimpleXmasStoryIdeas', 'csd', ['n=4'],'Napoleon Bonaparte', None, None]
tuple3 = ['SimpleXmasStoryIdeas', 'csd', ['n=5'],'from the perspective of the infant Jesus', None, None]
tuple_list = ['tuplelist1',tuple1, tuple2, tuple3]
tuple4 = ['CreatePersonBackstory', 'gpt3complete', 'n=3','\n$NAME will be born in the area currently known as Russia in the year 3000 CE.\n', None, None]
tuple_list = ['NFTmaker', tuple4 ]
class Longform:
    def __init__(self, list_of_preset_tuples, output_dir):
        self.list_of_preset_tuples = list_of_preset_tuples
        self.output_dir = output_dir

        return

    def data_dir(output_dir):
        output_dir = 'app/data/longform_test'
        return output_dir

    def set_defaults(self):
# set
        return

    def create_longform(list_of_preset_tuples, output_dir):
        datadir = output_dir + '/' + list_of_preset_tuples[0] + '_' + str(uuid4())[0:4]
        print('datadir is: ' + datadir)
        for preset, completion_type, parameters, prompt, function4each, functionatend in list_of_preset_tuples[1:]:
            print(preset, completion_type, parameters, prompt, function4each, functionatend)
            for parameter in parameters:
                #print(parameter)
                if parameter.startswith("n="):
                    n = parameter.split("=")[1]
                    #print('n is', n)
            if completion_type == 'gpt3complete':
                print('ppp:', preset,  prompt, parameters)
                response = gpt3complete(preset, parameters, prompt)
                openai_response = response[0]
                text = openai_response['choices'][0]['text']
                print('text is', text)
            elif completion_type == 'csd':
               # print('got to csd', 'preset is', preset, 'parameters are', parameters, 'prompt is', prompt, 'datadir is', datadir)
                response = csd.main(article_writer_preset=preset,number=n, generate_articles=True, article_titles_only=True, article_title_prompt=prompt, datadir=datadir)
            elif completion_type == 'gpt3complete':
                gpt3complete.create_longform(preset, parameters, prompt, datadir)
            else:
                print('completion_type not recognized')
                return
        return

    create_longform(tuple_list, 'app/data/longform_test')
