import sys
import requests
import json
import nltk
import math

nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Global Variables
SEARCH_JSON_API_KEY = ""
SEARCH_ENGINE_ID = ""
TARGET_PRECISION = 0.0
QUERY = ""

stop_words = set(stopwords.words("english"))

def read_parameters():
    """
    Read parameters from command line and assign to global vars
    :return: void
    """
    inputs = sys.argv
    global SEARCH_JSON_API_KEY, SEARCH_ENGINE_ID, TARGET_PRECISION, QUERY

    SEARCH_JSON_API_KEY = inputs[1]
    SEARCH_ENGINE_ID = inputs[2]
    TARGET_PRECISION = float(inputs[3])
    QUERY = inputs[4]
    i = 5
    while i < len(inputs):
        QUERY += " " + inputs[i]
        i += 1

    # Print to console
    print ("Search Key: " + SEARCH_JSON_API_KEY)
    print ("Search Engine ID: " + SEARCH_ENGINE_ID)
    print ("Target Precision: " + str(TARGET_PRECISION))
    print ("QUERY: " + QUERY)


def google_search():
    """
    Return the Top-10 results of Google search using QUERY
    :return: list
    """
    results = []

    
    # Google search
    url = "https://www.googleapis.com/customsearch/v1?key=" + SEARCH_JSON_API_KEY + "&cx=" + SEARCH_ENGINE_ID + "&q=" + QUERY
    response = requests.get(url)
    search_results = json.loads(response.text)['items']

    # Extract info and format results
    for item in search_results:
        title = item['title']
        url = item['link']
        summary = item['snippet']

        item_data = {
            "title": title,
            "url": url,
            "summary": summary,
            "relevant": False
        }
        results.append(item_data)

    return results


def collect_user_feedback():
    """
    Collect the feedback of user, every result is marked relevant or not
    :return: precision(float)
    """
    search_results = google_search()

    for idx in range(len(search_results)):
        item = search_results[idx]
        print ("Result " + str(idx + 1))
        print ("[")
        print (" URL: " + item['url'])
        print (" Title: " + item['title'])
        print (" Summary: " + item['summary'])
        print ("]")

        feedback = raw_input("Relevant(Y/N)? ")
        if feedback == 'Y' or feedback == 'y':
            item['relevant'] = True
        print ("") # New line

    return search_results


def calculate_precision(search_results):
    """
    Calculate the precision based on feedback
    :param search_results: list of results(10)
    :return: precision(float)
    """
    count = 0
    for item in search_results:
        if item['relevant']:
            count = count + 1

    return count * 1.0 / 10


def show_feedback(precision, augmented_words):
    """
    Print the update feedback to console
    :param precision: float, augmented_words: list
    :return: void
    """
    global QUERY
    print ("FEEDBACK SUMMARY")
    print ("Query: " + QUERY)
    print ("Precision: " + str(precision))

    if precision < TARGET_PRECISION:
        print ("Still below the desired precision of " + str(TARGET_PRECISION))
        words = ""
        for word in augmented_words:
            words = words + " " + word
        print ("Augmenting by " + words)
        QUERY += " " + words
    else:
        print ("Desired precision reached, done")
    print ("") # New line


def find_augmented_words(search_results):
    """
    Find the words needed to augment query
    :param search_results: [{'title', 'url', 'summary', 'relevant'},...]
    :return: list of words
    """
    # TODO
    
    invertedList, search_results = indexer(search_results)
    
    queryWeights = rocchio(invertedList, search_results)
    
    curQueries = QUERY.split(" ")
    queryWeights_sorted_keys = sorted(queryWeights, key=queryWeights.get, reverse=True)
    i = 0
    newQueries = []
    for key in queryWeights_sorted_keys:
        if key in curQueries:
            continue
        newQueries.append(key)
        i += 1
        if i >= 2:
            break

    return newQueries
    
#     return ['test_word1', 'test_word2']

def indexer(search_results):
    """
    Construct index:
    https://nlp.stanford.edu/IR-book/html/htmledition/scoring-term-weighting-and-the-vector-space-model-1.html
    :param search_results: [{'title', 'url', 'summary', 'relevant'},...]
    :ret invertedList:{'term'}, search_results: [{'title', 'url', 'summary', 'relevant', 'df'},...]
    """

    tremFreq = {}
    invertedList = {}

    for idx in range(len(search_results)):
        item = search_results[idx]
        tokens = word_tokenize(item["summary"])
        tokens += word_tokenize(item["title"])
        filtered_tokens = [w.lower() for w in tokens if not w in stop_words and len(w) > 1]

        item['df'] = {}
        for token in filtered_tokens:
            item['df'][token] = item['df'].get(token, 0) + 1
#             tremFreq[token] = tremFreq.get(token, 0) + 1
            invertedList[token] = invertedList.get(token, set())
            invertedList[token].add(idx)

    return invertedList, search_results


def rocchio(invertedList, search_results):
    """
    Construct index:
    :param invertedList:{'term'}, search_results: [{'title', 'url', 'summary', 'relevant', 'df'},...]
    :ret queryWeights:{'term'}
    """
    
    alpha = 1
    beta = 0.75
    gamma = 0.15

    queryWeights = {}
    prevQuery = QUERY.split(" ")
    for term in prevQuery:
        queryWeights[term] = 1.0

    weights = {}
    for term in invertedList.iterkeys():       
        weights[term] = 0.0

    relevantDf = {}
    nonrelevantDf = {}
    numRel = 0
    numNonrel = 0
    for idx in range(len(search_results)):
        item = search_results[idx]

        if item["relevant"]:
            numRel += 1
            for term in item["df"]:
                relevantDf[term] = relevantDf.get(term, 0) + item["df"][term];
        else:
            numNonrel += 1
            for term in item["df"]:
                nonrelevantDf[term] = nonrelevantDf.get(term, 0) + item["df"][term];


    # Rocchio algotithm
    for term in invertedList.iterkeys():
        idf = math.log(float(len(search_results)) / float(len(invertedList[term])), 10)

        for idx in invertedList[term]:
            if search_results[idx]['relevant']:
                weights[term] = weights[term] + beta * idf * (float(relevantDf[term]) / numRel)
            else:
                weights[term] = weights[term] - gamma * idf * (float(nonrelevantDf[term]) / numNonrel)

        if term in queryWeights:
            queryWeights[term] = alpha * queryWeights[term] + weights[term]
        elif weights[term] > 0:
            queryWeights[term] = weights[term]

    return queryWeights

def main():
    read_parameters()

    # First iteration
    print ("Google Search Results:")
    print ("======================")
    search_results = collect_user_feedback()
    precision = calculate_precision(search_results)
    augmented_words = find_augmented_words(search_results)
    show_feedback(precision, augmented_words)

    # Loop until condition satisfy
    while ((precision - 0.0) > 0.000001) and (precision < TARGET_PRECISION):
        search_results = collect_user_feedback()
        precision = calculate_precision(search_results)
        augmented_words = find_augmented_words(search_results)
        show_feedback(precision, augmented_words)
        
        
if __name__ == '__main__':
    main()