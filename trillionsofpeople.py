import streamlit as st
import streamlit.components.v1 as components
import glob
import os
import csv
import fitz

from yaml import unsafe_load
import fakeface

if st.secrets['environment'] == 'cloud':
    print('running on Streamlit Cloud with secrets file, gpt3 reduced fx, and no quota tracking')
    datadir = 'people_data'
elif st.secrets['environment'] == 'local':
    print("running on Fred's mac with reduced gpt3 fx, secrets file and no quota tracking")

    datadir = 'people_data'
elif st.secrets['environment'] == 'self-hosted':
    print('running  self-hosted on AWS instance with reduced gpt3 fx, secrets file, and no quota tracking')
    datadir = 'people_data'

import gibberish
from numpy import extract, subtract

st.set_page_config(layout="wide")
import pandas as pd
import datetime
from datetime import date
from gpt3_reduced_fx import gpt3complete, presets_parser, post_process_text, construct_preset_dict_for_UI_object
from utilities import show_current_version
from nltk.corpus import wordnet as wn
import random

import requests
from gibberish import Gibberish
gib = Gibberish()

import csv

@st.experimental_memo
def cacheaware_gpt3complete(preset, prompt, username="trillions"):
    response = gpt3complete('CreatePersonBackstory', prompt, username)
    return response


def load_people():
    all_people_data = pd.DataFrame()
    csvtarget = 'trillions-deploy/people_data/' +  '*.csv'
    for i in glob.glob(csvtarget):
        print("reading file ", i)
        i_df = pd.read_csv(i, index_col=0, squeeze=True)
        all_people_data = all_people_data.append(i_df)
    return all_people_data


def import_data(dfname):
    df = pd.read_csv(dfname, index_col=0, squeeze=True)
    # fill missing fourwordsname with fourwordsnames
    df['fourwordsname'] = df['fourwordsname'].fillna(df['fourwordsname'].apply(fourwordsname))
    # fill missing species with species
    df['species'] = df['species'].fillna(df['species'].apply(random.choice(['sapiens', 'neanderthalensis', 'denisovan', 'floresiensis']) ))
    # fill missing OCEANtuple with OCEANtuple
    df['OCEANtuple'] = df['OCEANtuple'].fillna(df['OCEANtuple'].apply(OCEANtuple(species)))
    # fill remaining nas with NaN
    df = df.fillna(value=np.nan)
    return df

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

def OCEANtuple(species):
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
    timelines = ['ours', 'RCP 8.5', 'Earth-616', 'Earth-1218', 'ODNI2040']
    # timelinfo_dict
    return timeline_info

def assign_realness_status(data_source):
    if data_source == 'OpenAI':
        realness = 'synthetic'
    elif data_source == 'historical':
        realness = 'authenticated'
    elif data_source == 'fictional':
        realness = 'fictional'
    elif data_source == 'random':
        realness = random.random.choice['synthetic', 'authenticated', 'fictional']
    else:
        realness = 'unknown'
    return realness

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

def migration_to(latitude, longitude, nearest_city):
    # migration function -- typically least travel cost + 20-500 km
    to_latitude_offset, to_longitude_offset, to_nearest_city_offset = 0, 0, 0
    current_location = latitude + to_latitude_offset, longitude + to_longitude_offset, nearest_city + to_nearest_city_offset
    return current_location

def select_fake_face_file():
    fakefiledir = datadir + '/' + 'fake'
    fakefilepath = fakefiledir + '/' + '*.jpg'
    fake_face_files = glob.glob(fakefilepath)
    #st.write(fake_face_files)
    image_filename = random.choice(fake_face_files)
    return image_filename

def fetch_fake_face_api(gender, min_age=10, max_age=70):
    baseuri = "https://fakeface.rest/thumb/view?"
    gender=gender
    noise = str(random.randint(1,99))
    face_thumb_uri = baseuri + noise + '/' + gender 


    return face_thumb_uri

#def create_single_person(preset, target_year, country):

def create_scenario_personas(scenario, n, target_year, country):

    
    #scenario_personas_df = pd.DataFrame(columns=peopledf_columns)
    scenario_personas_data =[]
    card_columns = ['Attributes']
    card_df = pd.DataFrame(columns=card_columns)
    card_df['Attributes'] = peopledf_columns
    scenario_personas = {}
    
    for person in range(n):
        values = []

        latitude, longitude, nearest_city = random_spot(countries[country])
        species =  'sapiens'
        gender = random.choice(['male', 'female'])
        shortname = create_shortname(species)
        year_of_birth_in_CE = target_year
        thisperson4name = fourwordsname()
        timeline = 'ours'
        realness = 'synthetic' # ['synthetic', 'authenticated', 'fictional']
        #OCEAN_tuple =  'test' # OCEANtuple()
        backstory = ""
        #cues = "job, etc."
        prompt = 'Biographical details: ' + gender + ':' + country 
        backstory  = gpt3complete(scenario_selected, prompt,'trillions')[0]['choices'][0]['text']
        image_uri = "<img src=" + '"' + fetch_fake_face_api(gender) + '"' + ' height=90' + ">"

        source = scenario
        comments = ""
        status =  'Register | Edit | Claim '
        values = [  shortname, image_uri,year_of_birth_in_CE, gender, species, timeline, realness, latitude, longitude, nearest_city, country, backstory, thisperson4name, source, comments, status]#, OCEAN_tuple]
        zipped = zip(peopledf_columns, values)
        scenario_personas_dict = dict(zipped)
        scenario_personas_data.append(scenario_personas_dict)
        card_df["Values"] = values
        pd.set_option('display.max_colwidth', 70)  


    scenario_personas_df = pd.DataFrame(scenario_personas_data, columns = peopledf_columns)

    return scenario_personas_df, card_df

# load files & initialize variables at startup

filename = datadir + '/' + 'country.csv'

countries_df = pd.read_csv(datadir + '/' + 'country.csv', names =['country_name', 'code'],  index_col=0, squeeze=True)
countries_list = countries_df.index.tolist()
countries = countries_df.to_dict()
comments = 'This is a comment'
status = 'Register : Edit | Claim'

peopledf_columns = ['name', 'image', 'born', 'gender','species', 'timeline', 'realness', 'latitude', 'longitude', 'nearest_city', 'country', 'backstory', 'fourwordsname', 'source','comments', 'status' ]#  'OCEANtuple'])

st.title('TrillionsOfPeople.info')
st.markdown("""_One row for every person who ever lived, might have lived, or may live someday._

_**Create, edit, register, claim, share **stories about your fellow souls._

_A tool to explore the human story._

The best available estimate is that about 117 billion unique humans have ever lived on Earth. [(Population Reference Bureau, 2021).](https://www.prb.org/articles/how-many-people-have-ever-lived-on-earth/) With new people being born at rate of about 133 million/year, this number is expected to rise to 121 billion by 2050, about 129 billion by 2100, and, trends continuing, 250 billion by the year 3000 CE and one trillion by the year 9000 CE. An optimist may hope that eventually there will be trillions of human lives. The numbers become even larger when you add mythic and fictional characters, who have been born and died thousands of times, and have some of the most interesting stories.

Sadly, the details of most of those lives are lost in the shadows of past and future. Many millenia of human history are shrouded in near-complete mystery.  (Graeber 2021). WikiBio dataset derived from Wikipedia's "biographical persons" category has about 784,000 records; but only 200 of those are deemed "core biographies" by the WikiBio team and given top-tier treatment. (WikiBio 2021)  

This focus on a small percentage of all lives has important practical implications. Our understanding of lives in the past is mostly limited to those few persons for whom we have written records or concrete artifacts; most are mysteries--names, skeletons, or less. Similarly, one of the major difficulties in implementing far-sighted energy and climate policies is that future people are abstractions. 

_Trillions_ is a tool to make both past and futures feel more real, using state-of-the-art scientific, historical, and artificial intelligence techniques.You, as an individual, can explore the lives of real-seeming people--past, present, or future--in small numbers or large--and connect them with your personal story.  You, as an organizational leader, can quickly create and iterate through and personas that will give new energy and focus to your organization's forward-looking vision.

""")
st.sidebar.markdown(""" ## Navigation

- [Explore Scenarios](#explore-scenarios)
- [Create People From Any Era](#create-people)
- [Browse People](#browse-people)
- [Submit Data](#submit-data)
- [Methods](#methods)
- [Data Dictionary](#data-dictionary)
- [References](#references)""")


st.sidebar.markdown("""## Partners

This project needs beta users, demographers, futurists, historians, anthropologists, coders, GIS specialists, designers, data providers, sponsors, and investors! Please contact me at [fredz@trillionsofpeople.info](mailto:fredz@trillionsofpeople.info). 

--Fred Zimmerman, Founder""")
st.sidebar.markdown(""" **Version Information** """)

version_trillions = show_current_version()
st.sidebar.write(version_trillions, collapsed=True)

twoblock =  st.sidebar.columns([1,1])

with st.sidebar:
    
    twoblock[0].write("Spread the word!")
    with twoblock[1]:
        components.html("""
    <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" 
    data-text="Share TrillionsOfPeople.info:8502🎈" 
    data-url="https://trillionsofpeople.info:8502"
    data-show-count="false">
    data-size="Large" 
    data-hashtags="streamlit,python"
    Tweet
    </a>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """)

st.subheader('Explore Scenarios')

st.markdown(""" You can choose from a variety of scenarios to explore. The first set of [scenarios](https://www.dni.gov/index.php/gt2040-home/scenarios-for-2040) is drawn from the Office of the Director of National Intelligence's _Global Trends 2040_ (ODNI 2021), a planning and visioning exercise that the US Intelligence conducts every five years. The next set will be drawn from the IPCC's Representative Concentration Scenarios, which chart possible GHG futures for the year 2100.  In future, you will be able to submit scenarios to the project yourself.""")

with st.form("Scenario Explorer"):
    scenario_list = ['GlobalTrends2040RD', 'GlobalTrends2040AWA', 'GlobalTrends2040CC', 'GlobalTrends2040SS', 'GlobalTrends2040SSpb','GlobalTrends2040TM']
    scenario_dict ={}
    if scenario_list:
        scenario_dict = construct_preset_dict_for_UI_object(scenario_list)
    scenario_selected = st.selectbox('Choose a scenario', scenario_list, index=0, format_func = lambda x: scenario_dict.get(x))

    selected_presetdf = presets_parser(scenario_selected)[0]
 
    scenario_name = selected_presetdf['preset_name'].iloc[0]
    n = st.slider("Select number of personas to build", 1, 5, value=1, help="To build larger numbers of personas, contact Fred Zimmerman.")
    submitted = st.form_submit_button('Create Scenario Personas')
    scenario_row_values, show_personas = [], []
    random_country = random.choice(countries_list)
    if submitted:
        infomessage = f"Creating {n} personas for {scenario_name}."
        st.info(infomessage)
        if scenario_selected:
            #scenario_personas_df = create_scenario_personas(scenario_selected, 1, 2040, random_country)[0]
            card_df = create_scenario_personas(scenario_selected, 1, 2040, random_country)[1]
        if not card_df.empty:
            #show_personas = scenario_personas_df.drop(axis=1, columns=['gender', 'invisible_comments'])
            st.write(card_df.to_html(escape=False), unsafe_allow_html=True)
            
           
        else:
            st.error("Backend problem creating personas, contact Fred Zimmerman for help.")

    else:
        pass


st.subheader("Create People From Any Era")

with st.form("my_form"):

    year = st.number_input('Specify birth year as a positive value in the Common Era or a negative value in the period Before Common Era.', min_value=-150000, max_value=10000, value=2100, step=100, help='The year 700 BCE is -700, the year 2100 CE is 2100.')

    infomessage = ''

    today = datetime.datetime.now()
    if year <0:
        target_year = -1 * year 
        infomessage = 'Year of birth is ' + str(target_year) + ' BCE.'
    elif year == 0:
        infomessage = 'It is ' + str(year) + 'CE.'
        target_year = year
    if year > 0:
        infomessage = 'It is ' + str(year) + ' CE.'
        target_year = year

    latitude,longitude, nearest_city = 0, 0, "Unknown"
    #indexcountry = random.randrange(0, len(countries_list))
    #st.write(indexcountry)
    country = st.selectbox('Pick the territory of a modern country.', options=countries.keys(), help ='Unknown locations are retrieved occasionally during peak hours.')
    
    if country == 'Random':
        country = random.choice(countries_list)
        infomessage = 'Randomly chosen: ' + country + '.'

    else:
        infomessage = 'Country is ' + country + '.'


    j = int(st.number_input('How many people do you want to generate? [For batch jobs, contact Fred Zimmerman.]', value=1, min_value=1, max_value=5, step=1, help='Processing time is linear with the number of people generated.'))
   
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.info(infomessage)
#st.write('submitting', country)

        peopledf = pd.DataFrame(columns=peopledf_columns)
        peopledata =[]
        card_columns = ['Attributes']
        card_df = pd.DataFrame(columns=card_columns)
        card_df['Attributes'] = peopledf_columns

    # with form info in hand, create personas

        for i in range(j):

            species =  'sapiens'
            gender = random.choice(['male', 'female'])
            shortname = create_shortname(species)
            year_of_birth_in_CE = target_year
            thisperson4name = fourwordsname()
            timeline = 'ours'
            realness = 'synthetic' # ['synthetic', 'authenticated', 'fictional']
            #OCEAN_tuple =  'test' # OCEANtuple()
            if year < 0:
                prompt = shortname + ' was born ' + str(year_of_birth_in_CE) + 'years ago in  the area now known as ' + country + '.'
            if year == 0:
                prompt = shortname + ' was born in the area now known as ' + country + '.'
            if year > 0:
                prompt = shortname + ' will be born in the area now known as ' + country + '.'
            source = 'TOP.info'
            username = 'trillions'
            latitude, longitude, nearest_city = random_spot(country)
            prompt = prompt + '\n\n'
            response = gpt3complete('CreatePersonBackstory', prompt, username)
            openai_response= response[0]
            backstory = openai_response['choices'][0]['text']
            image_filename = "<img src=" + '"' + fetch_fake_face_api(gender) + '"' + ' height=90' + ">"
            #st.write(backstory)
            
            values = [shortname, image_filename, year_of_birth_in_CE, gender, species, timeline, realness, latitude, longitude, nearest_city, country, backstory, thisperson4name, source, comments, status]#,
            card_df[shortname] = values
            zipped = zip(peopledf_columns, values)
            people_dict = dict(zipped)
            peopledata.append(people_dict)
            

        pd.set_option('display.max_colwidth', 70)  
        peopledf = peopledf.append(peopledata)
        #st.write(peopledf)

        if st.secrets['environment'] == 'cloud':
            pass
        else:
            backupfilepath = datadir + '/' + 'backup.csv'
            peopledf.to_csv(backupfilepath, mode='a', header=False, index=False, quoting=csv.QUOTE_ALL)

        #show_created_people = peopledf.drop(axis=1, columns=['gender', 'comments'])

        if not card_df.empty:

            st.write(card_df.to_html(escape=False), unsafe_allow_html=True)

            card_df.to_html('out.html')
            html = fitz.open('out.html')
            pdfbytes = html.convert_to_pdf()
            pdf = fitz.open("pdf", pdfbytes)
            pdf.save("some.pdf")

        else:
            st.error("Backend problem creating personas, contact Fred Zimmerman for help.")

# New section

st.subheader("Browse People")
st.write('This section contains historical, fictional, and synthetic personas.')
people = browse_people(datadir + '/' + 'people.csv')
peopledf = pd.DataFrame(people)
browsepeopledf = pd.DataFrame(people)
st.dataframe(browsepeopledf.head(5))


st.subheader("Submit data")
st.markdown("""To load, or request the creation of, real, fictitious, or hypothetical people with particular characteristics, please contact Fred Zimmerman.  Upload options coming.""")

st.subheader("Methods")

st.markdown(""" The guiding principle of "one row per person" implies that the number of columns must be kept manageably low. There may be a time where a great profusion of data tables and models is needed to capture vast amounts of data about each individual and their relations to one another and to the physical and social worlds, but the initial goal is to be as parsimonious  as possible. """)

st.subheader("Data Dictionary")

data_dictionary = { "shortname" : "Short names are programmatically created and intended to be as culture- and gender-agnostic as possible.",
"image":"Currently provided via FakeFace API; it's understood that the images are not necessarily very consistent with the other biographical information for the persona. Future versions of this service will include a more robust image generation service.",
"year_of_birth_in_CE" : "Year of birth in the Common Era, negative values are BCE, positive values are CE.", 
"gender" : "Gender is assigned programmatically as socially constructed during the individual's lifetime and consistent with self-chosen preferences. Child-bearing capacity, important for demographic models, will be addressed separately in future development.",
"species": "At least four hominin species inhabited Earth during our time window of 190,000 BCE to 10,000 CE: 'sapiens', 'neanderthalensis', 'denisovan', 'floresiensis'.  It is possible that there will be new species or species-like entities in the future, such as AIs or cyborgs.",
"timeline" : "The database allows for representing persons possibly found in alternate timelines.",
"realness": "Types of realness include 'synthetic', 'historic', 'documented' and 'fictional.'",
"latitude" : "Self-explanatory.",
"longitude": "Self-explanatory.",
"nearest_city" : "Nearest present-day city.",
"backstory" : "Created by a language model in response to a prompt written by Fred Zimmerman.",
"thisperson4name" : "Four words that provide a unique identifier for well in excess of a trillion persons.",
"comments" : "Free text; may be from any source including _Trillions_, data provider, or users.",
"source" : "The organization that provided the definition for the persona.", 
"status" : "Registration allows users to add newly created persons to the permanent database.   Editing enables users to recommend or request changes to personas. And claiming allows users to 'own' a historic, synthetic or (public domain) fictional persona connected to non-fungible tokens (NFTs), i.e. collectible cards authenticated via the blockchain." }

st.write(data_dictionary)
st.subheader("References")

# open file with references
with open('trillionsofpeople.info.txt', 'r') as f:
    st.markdown(f.read())
