from gensim import utils
import json
import time

start = time.time()
count = 0
filename = 'app/data/enwiki-latest.json.gz'
with utils.open(filename, 'rb') as f:
    for line in f:
        # decode each JSON line into a Python dictionary object
        article = json.loads(line)
        count = count + 1
        if (count % 100000) == 0:
            print(count)
            print(time.time() - start)
        # each article has a "title", a mapping of interlinks and a list of "section_titles" and
        if article['title'].startswith("A"):
            #print(article['title'])
            #print(article['text'])
            #print("\n")
            pass
        else:
            pass
            #print("not printing articles beginning with B-Z")
        #print("Article title: %s" % article['title'])
        # #print("Interlinks: %s" + article['interlinks'])
        # for section_title, section_text in zip(article['section_titles'], article['section_texts']):
        #     print("Section title: %s" % section_title)
        #     print("Section text: %s" % section_text)