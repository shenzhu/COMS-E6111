import sys
import requests
import json


# Global Variables
SEARCH_JSON_API_KEY = ""
SEARCH_ENGINE_ID = ""
TARGET_PRECISION = 0.0
QUERY = ""


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

    # Print to console
    print "Search Key: " + SEARCH_JSON_API_KEY
    print "Search Engine ID: " + SEARCH_ENGINE_ID
    print "Target Precision: " + str(TARGET_PRECISION)
    print "QUERY: " + QUERY


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
        print "Result " + str(idx + 1)
        print "["
        print " URL: " + item['url']
        print " Title: " + item['title']
        print " Summary: " + item['summary']
        print "]"

        feedback = raw_input("Relevant(Y/N)? ")
        if feedback == 'Y':
            item['relevant'] = True
        print "" # New line

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
    print "FEEDBACK SUMMARY"
    print "Query: " + QUERY
    print "Precision: " + str(precision)

    if precision < TARGET_PRECISION:
        print "Still below the desired precision of " + str(TARGET_PRECISION)
        words = ""
        for word in augmented_words:
            words = words + " " + word
        print "Augmenting by " + words
    else:
        print "Desired precision reached, done"
    print "" # New line


def find_augmented_words(search_results):
    """
    Find the words needed to augment query
    :param search_results: [{'title', 'url', 'summary', 'relevant'},...]
    :return: list of words
    """
    # TODO
    return ['test_word1', 'test_word2']


def main():
    read_parameters()

    # First iteration
    print "Google Search Results:"
    print "======================"
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
