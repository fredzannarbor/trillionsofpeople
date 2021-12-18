import gibberish
from numpy import extract, subtract
import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import datetime
from datetime import date
from gpt3complete import gpt3complete, presets_parser, post_process_text
from nltk.corpus import wordnet as wn
import random

import requests
from gibberish import Gibberish
gib = Gibberish()

import csv

@st.experimental_memo
def cacheaware_gpt3complete(preset, prompt, username="guest"):
    response = gpt3complete('CreatePersonBackstory', prompt, username="guest")
    return response

def read_csv(filename):
    countries = pd.read_csv(filename, names =['code', 'country_name'],  index_col=0, squeeze=True).to_dict()
    return countries

def browse_people(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        people = list(reader)
    return people

def create_shortname(species):
    if species == 'sapiens':
        shortname = gib.generate_word()
    elif species == 'neanderthalensis':
        # add subprocess to call short names
        shortname = gib.generate_word(start_vowel=False)
    else:
        shortname = gib.generate_word()
    #name='Sapiens'
    shortname = shortname.title()
    return shortname

def fourwordsname():
    # verdant apples luxuriating fiercely

    with open('app/utilities/moby_pos/adjectives_clean.txt') as f:
        adjectives= f.readlines()
        f.close()
    with open('app/utilities/moby_pos/nouns_clean.txt') as f:
        nouns= f.readlines()
        f.close()
    with open('app/utilities/moby_pos/verbs_clean.txt') as f:
        verbs= f.readlines()
        f.close()
    with open('app/utilities/moby_pos/adverbs_clean.txt') as f:
        adverbs= f.readlines()
        f.close()
    
    
    words = adjectives
    short_adjectives  = [word for word in words if 4 < len(word) < 9]
    adjective = random.choice(short_adjectives).strip()
    noun = random.choice(nouns).strip()
    verb = random.choice(verbs).strip()
    adverb = random.choice(adverbs).strip()

    print(adjective, noun, verb, adverb)
    fourwordsname = adjective + '-' + noun + '-' + verb + '-' + adverb
    return fourwordsname

def OCEANtuple():
    openness = random.random()
    conscientiousness = random.random()
    extraversion = random.random()
    agreeableness = random.random()
    emotional_range = random.random()
    OCEANtuple = (openness, conscientiousness, extraversion, agreeableness, emotional_range)
    return OCEANtuple

def get_species_info(species_name):
    known_species = ['sapiens', 'neanderthalensis', 'denisovan', 'floresiensis']
    # specifies_info_dict
    return species_info

def get_timeline_info(timeline):
    timelines = ['ours', 'RCP 8.5', 'Earth-616', 'Earth-1218']
    # timelinfo_dict
    return timeline_info


def random_spot(country):
    latitude, longitude, nearest_city = "Unknown", "Unknown", "Unknown"
    try:
        request_uri = "https://api.3geonames.org/?randomland=" + country + '&json=1'
        print(request_uri)
        resp = requests.get(request_uri)
        json = resp.json()
        print(json)
        nearest_city = json['nearest']['name']
        latitude = json['nearest']['latt']
        longitude = json['nearest']['longt']
        print(nearest_city, latitude, longitude)
    except Exception as e:
        print(e)
        nearest_city = 'Unknown'
        latitude = 'Unknown'
        longitude = 'Unknown'
    return latitude, longitude, nearest_city

filename = 'country.csv'

countries = read_csv(filename)

st.title('TrillionsofPeople.info')
st.markdown("""_Generate synthetic people for a given location and time._

The best available estimate is that about 117 billion unique humans have ever lived on Earth. [(Population Reference Bureau, 2021).](https://www.prb.org/articles/how-many-people-have-ever-lived-on-earth/) With new people being born at rate of about 133 million/year, this number is expected to rise to 121 billion by 2050, about 129 billion by 2100, and, trends continuing, 250 billion by the year 3000 and one trillion by the year 9,000 CE. An optimist may hope that eventually there will be trillions of human lives. Sadly the details of most of those lives are lost in the shadows of past and future.  

This has very practical implications. For example, one of the major difficulties in dealing with climate change policy is that future people seem like abstractions.  Similarly, our understanding of lives in the past is mostly limited to those few for whom we have written records or concrete artifacts.

This is a tool to make those lives feel more real, using state-of-the-art scientific, historical, and artificial intelligence techniques.  Using our friendly no-code UI you can create a synthetic population of real-seeming people, in small numbers or large, and save, share, and register your synthetic people.  You can even use the same techniques to explore the lives of authenticated historical people!
""")

st.subheader("Browse People")
people = browse_people('people.csv')
st.table(people)

st.subheader("Create People")

with st.form("my_form"):


    year = st.number_input('Specify birth year as a date Common Era or Before Common Era, with 1 AD = 1 CE.', min_value=-150000, max_value=10000, value=2100, step=100)

    infomessage = ''

    today = datetime.datetime.now()
    if year <0:
        target_year = year + today.year
        infomessage = 'Your people will be generated with year of birth as ' + str(target_year) + ' BCE.'
    elif year == 0:
        infomessage = 'It is ' + str(year) + 'CE.'
        target_year = year
    if year > 0:
        infomessage = 'It is ' + str(year) + ' CE.'
        target_year = year

    latitude,longitude, nearest_city = "Unknown", "Unknown", "Unknown"
    indexcountry = random.randrange(0, len(countries))
    country = st.selectbox('Pick a location that corresponds to a modern country.', options=countries.keys(), help ='Unknown locations are retrieved occasionally during peak loS.')

    j = st.number_input('How many people do you want to generate? [For batch jobs, which may be of any size, contact Fred Zimmerman.]', value=1, min_value=1, max_value=5, step=1, help='Processing time is proportional to number of people generated.')
   
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        #st.write('You selected:', country)
        latitude, longitude, nearest_city = random_spot(countries[country])


peopledf_columns = ['name', 'born', 'species', 'timeline', 'latitude', 'longitude', 'nearest_city', 'backstory', 'fourwordsname']#]], 'OCEANtuple'])

peopledf = pd.DataFrame(columns=peopledf_columns)
peopledata =[]

for i in range(j):
    species =  'sapiens'
    shortname = create_shortname(species)
    year_of_birth_in_CE = target_year
    thisperson4name = fourwordsname()
    timeline = 'ours'
    #OCEAN_tuple =  'test' # OCEANtuple()
    if year < 0:
        prompt = shortname + ' was born ' + str(year_of_birth_in_CE) + 'years ago in  the area now known as ' + country + '.'
    if year == 0:
        prompt = shortname + ' was born in the area now known as ' + country + '.'
    if year > 0:
        prompt = shortname + ' will be born in the area now known as ' + country + '.'

    response = cacheaware_gpt3complete('CreatePersonBackstory', prompt, username='guest')
    openai_response= response[0]
    backstory = openai_response['choices'][0]['text']
    values = [shortname, year_of_birth_in_CE, species, timeline, latitude, longitude, nearest_city, backstory, thisperson4name]#, OCEAN_tuple]
    zipped = zip(peopledf_columns, values)
    people_dict = dict(zipped)
    peopledata.append(people_dict)

pd.set_option('display.max_colwidth', 70)  
peopledf = peopledf.append(peopledata)

if submitted:
    st.info(infomessage)
    st.table(peopledf)
