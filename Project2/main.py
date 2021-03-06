import json
import requests
import sys
from bs4 import BeautifulSoup
from NLPCore import NLPCoreClient
import os
import re


class InformationExtractionEngine:
    def __init__(self):
        self.relation_map = {1: "Live_In", 2: "Located_In", 3: "OrgBased_In", 4: "Work_For"}
        
        self.entity_map = {1:['PEOPLE', 'LOCATION'], 2:['LOCATION', 'LOCATION'], 3:['ORGANIZATION', 'LOCATION'], 4:['PEOPLE', 'ORGANIZATION']}

        self.queries = set()
        
        # (word1, word2) -> (entity1, entity2, relation, prob)
        self.X = {}

        # Parameters from input
        self.SEARCH_JSON_API_KEY = ""
        self.SEARCH_ENGINE_ID = ""
        self.RELATION = 0
        self.THRESHOLD = 0
        self.QUERY = ""
        self.k = 0

        # Retrieved set
        self.retrieved_url = set()

        # Client
        self.client = NLPCoreClient(os.path.abspath("stanford-corenlp-full-2017-06-09"))

    def find_entities(self, sentences):
        """
        Find the name entities in a list of sentence, serving as the first pipine
        :return: list of entities
        """
        entities = []

        properties = {
            "annotators": "tokenize,ssplit,pos,lemma,ner",
            "parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
            "ner.useSUTime": "0"
        }
        doc = self.client.annotate(text=sentences, properties=properties)

        for sentence in doc.sentences:
            for token in sentence.tokens:
                if token.ner != 'O':
                    entities.append(token.ner)

        return entities

    def extract_relation_from_page(self, sentences):
        """
        Extract relation from sentence list(retrieved from a webpage), if satisfy condition(threshold and RELATION type), update relations
        :return: void
        """
        properties = {
            "annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation",
            "parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
            "ner.useSUTime": "0"
        }
        doc = self.client.annotate(text = sentences, properties = properties)

        # print doc.tree_as_string()

        for sentence in doc.sentences:
            for relation in sentence.relations:
                try:
                    probs = relation.probabilities
                    # Find max relation and corresponding max prob
                    max_relation = max(probs.iterkeys(), key = (lambda key : probs[key]))
                    max_prob = probs[max_relation]
                    # If max prob over threshold and max relation equals to curr relation, update relations
                    if max_prob > self.THRESHOLD and max_relation == self.relation_map[self.RELATION]:
                        key = (relation.entities[0].value, relation.entities[1].value)
                        
                        # judge the type of inputs
                        if float(max_prob) >= float(self.THRESHOLD) and self.entity_map[self.RELATION][0] == relation.entities[0].type and self.entity_map[self.RELATION][1] == relation.entities[1].type:
                            if key not in self.X or float(self.X[key][3]) < float(max_prob):
                                self.X[key] = (relation.entities[0].type, relation.entities[1].type, max_relation, max_prob)
                                print "Sentence:",
                                for token in sentence.tokens:
                                    print " " + token.word,
                                print ""

                                print "Relation Type: {0:10}| Confidence: {1:.3f}  | EntityType1: {2:15} | EntityValue1: {3:15} | EntityType2: {4:15} | EntityValue2: {5:15}".format(max_relation, float(max_prob), relation.entities[0].type, relation.entities[0].value, relation.entities[1].type, relation.entities[1].value)
                except:
                    pass

    def extract_relation(self):
        """
        This function executes each iteration
        1. Google Search and get a list of sentences for each url
        2. First pipeline, find entities and identify page
        3. If pass, second pipeline, extract relation and update relations
        :return:
        """
        web_pages = self.google_search()
        # print "Web Page Retrieved"
        for page in web_pages:
            entities = self.find_entities(page)
            # print entities
            if self.identity_page(entities):
                # print "Page Identified"
                self.extract_relation_from_page(page)
                # print "Page Processed"

    def identity_page(self, entities):
        """
        Check entities from one retrieved web page contains required entities for its r
        :return: boolean
        """
        if self.RELATION == 1:
            # Live_In
            if 'PERSON' in entities and 'LOCATION' in entities:
                return True
            else:
                return False
        elif self.RELATION == 2:
            # Located_In
            location_count = 0
            for entity in entities:
                if entity == 'LOCATION':
                    location_count += 1
            if location_count < 2:
                return False
            else:
                return True
        elif self.RELATION == 3:
            # OrgBased_In
            if 'ORGANIZATION' in entities and 'LOCATION' in entities:
                return True
            else:
                return False
        elif self.RELATION == 4:
            # Work_For
            if 'ORGANIZATION' in entities and 'PERSON' in entities:
                return True
            else:
                return False

    def google_search(self):
        """
        Return the Top-10 results of Google search using QUERY
        :return: list
        """
        results = []

        # Google search
        url = "https://www.googleapis.com/customsearch/v1?key=" + self.SEARCH_JSON_API_KEY + "&cx=" + self.SEARCH_ENGINE_ID + "&q=" + self.QUERY
        response = requests.get(url)
        search_results = json.loads(response.text)['items']

        # Retrieve each url and extract plain text
        for item in search_results:
            item_url = item['link']
            if item_url not in self.retrieved_url:
                try:
                    text = self.extract_text_from_page(item_url)
                    results.append(text)
                except:
                    pass
            self.retrieved_url.add(item_url)

        return results

    def extract_text_from_page(self, url):
        """
        Extract plain text from a web page pointed by url
        :return: list of sentences(str)
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Kill all script ans style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # text = [chunk.decode('unicode_escape').encode('ascii','ignore') + "." for chunk in chunks if chunk]
        text = [chunk.encode('utf-8') + "." for chunk in chunks if chunk]

        sentences = []
        for t in text:
            sentences.extend( re.split(r' *[\.\?!][\'"\)\]]* *', t))
        results = [sentence + "." for sentence in sentences]
        
        return results

    def read_parameters(self):
        """
        Read parameters from command line and assign to global vars
        :return: void
        """
        inputs = sys.argv

        if len(inputs) < 7:
            self.usage()
            sys.exit(1)

        self.SEARCH_JSON_API_KEY = inputs[1]
        self.SEARCH_ENGINE_ID = inputs[2]
        self.RELATION = int(inputs[3])
        self.THRESHOLD = float(inputs[4])
        self.QUERY = inputs[5]
        self.k = int(inputs[6])

        # Print to console
        print ("Search Key: " + self.SEARCH_JSON_API_KEY)
        print ("Search Engine ID: " + self.SEARCH_ENGINE_ID)
        print ("RELATION: " + self.relation_map[self.RELATION])
        print ("THRESHOLD: " + str(self.THRESHOLD))
        print ("QUERY: " + self.QUERY)
        print ("# of Tuples: " + str(self.k))

    def usage(self):
        sys.stderr.write(
            """Usage: python main.py <SEARCH_JSON_API_KEY> <SEARCH_ENGINE_ID> <RELATION> <THRESHOLD> <QUERY> <k>.\n""")

    def run(self):
        self.read_parameters()
        ind = 1
        while len(self.X) < self.k:
            print("Iteration " + str(ind) + ": query - " + self.QUERY)
            self.extract_relation()
            sorted_X = sorted(self.X.items(), key = lambda (k, v): v[3], reverse = True)
            print("=====Relations=====")
            count = 0
            for t in sorted_X:
                count += 1
                if count > self.k:
                    break
                print "Relation Type: {0:10}| Confidence: {1:.3f}  | Entity #1: {2:15}| Entity #2: {3:15}".format(self.relation_map[self.RELATION], float(t[1][3]), t[0][0], t[0][1])
            
            for t in sorted_X:
                temp_query = t[0][0] + " " + t[0][1]
                if not temp_query in self.queries:
                    self.queries.add(temp_query)
                    break

            # Check if enters infinite loop
            if self.QUERY == temp_query:
                sys.stderr.write(
                    """Can not find enough relation instances, program ends. Please try another set of parameters.\n""")
                sys.exit(1)
            self.QUERY = temp_query
            ind += 1
            


if __name__ == "__main__":
    engine = InformationExtractionEngine()
    engine.run()
