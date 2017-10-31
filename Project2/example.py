from NLPCore import NLPCoreClient

text = ["Bill Gates works at Microsoft."]#, "Sergei works at Google."] # In actuality, you will want to input the cleaned webpage for the first pipeline, and a list of candidate sentences for the second.

text2 = ["Microsoft Corporation is an American multinational technology company with headquarters in Redmond, Washington, it develops, manufactures, licenses, supports and sells computer software, consumer electronics, personal computers, and services, its best known software products are the Microsoft Windows line of operating systems, the Microsoft Office suite, and the Internet Explorer and Edge web browsers, its flagship hardware products are the Xbox video game consoles and the Microsoft Surface tablet lineup, as of 2016, it is the world's largest software maker by revenue, and one of the world's most valuable companies."]

#path to corenlp
client = NLPCoreClient('stanford-corenlp-full-2017-06-09')
properties = {
	"annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation", #Second pipeline; leave out parse,relation for first
	"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
	"ner.useSUTime": "0"
	}
doc = client.annotate(text=text, properties=properties)


print doc.sentences[0].relations
for r in doc.sentences[0].relations:
    probs = r.probabilities
    print "================="
    print probs
    max_r = max(probs.iterkeys(), key = (lambda key : probs[key]))
    print max_r
    print r.entities[0], r.entities[0].value, r.entities[0].type
    print r.entities[1], r.entities[1].value, r.entities[1].type

#print doc.tree_as_string()

# for sentence in doc.sentences:
#     for md in sentence.MachineReading:
#         print md

# print type(doc)
# print doc.sentences[0]
# # print doc.sentences[1]
# # print doc.sentences[2]
# print doc.tree_as_string()
# # print(doc.sentences[0].relations[0])
# # print(doc.tree_as_string())