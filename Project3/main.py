import sys
import csv
from itertools import combinations

# Global Variables
MIN_SUP = 0.01
MIN_CONF = 0.5
# FILE_NAME = 'INTEGRATED-DATASET.csv'
FILE_NAME = 'test.csv'

def read_parameters():
    inputs = sys.argv

    global FILE_NAME, MIN_SUP, MIN_CONF
    FILE_NAME = inputs[1]
    MIN_SUP = float(inputs[2])
    MIN_CONF = float(inputs[3])

    # Print to console
    print "min_sup: " + str(MIN_SUP)
    print "min_conf: " + str(MIN_CONF)

def apriori_gen(L_prev):
    """
    Generate new candidates from large itemsets
    :return: Ck list of tuple
    """
    k = len(L_prev[0]) + 1
    Ck = set()
    for p in L_prev:
        for q in L_prev:
            c = set(list(p)) | set(list(q))
            if len(c) == k:
                x = tuple(sorted(list(c)))
                Ck.add(x)
    return Ck

def get_supports(L1, itemsets, transactions):
    """
    get supports that larger than MIN_SUP
    """
    L_prev = L1
    L = L1
    while len(L_prev) > 0:
        Ck = apriori_gen(L_prev)
        items = {} #{itemsets: count}
        for t in transactions:
            for c in Ck:
                if set(list(c)) <= set(t):
                    items[c] = items.get(c, 0) + 1
        
        L_cur = []
        for k, v in items.iteritems():
            if v >= MIN_SUP * len(transactions):
                L_cur.append(k)
                itemsets[tuple(k)] = v;

        L_prev = L_cur
        L += L_cur        
    return itemsets

def get_confidence(itemsets):
    """
    :return:     rules:{tuple(tuple(LHS), tuple(RHS)): confidence}
    """
    rules = {}
    for k, v in itemsets.iteritems():
        if len(k) > 1:
            for x in combinations(k, len(k)-1):
                conf = v / float(itemsets[x])
                if conf >= MIN_CONF:
                    rules[ (x, tuple(set(x) ^ set(k)))] = conf
    return rules

def apriori(transactions):
    """
    :param: list of transactions
    :return:
    itemsets: {tuple(items): sup_val}
    rules:{tuple(tuple(LHS), tuple(RHS)): confidence}
    """
    L1, itemsets = get_freq_1_itemset(transactions)
    itemsets = get_supports(L1, itemsets, transactions)
    rules = get_confidence(itemsets)
    return itemsets, rules


def get_freq_1_itemset(transactions):
    """
    get item set and 1-itemsets and 1-item larger itemset
    : return L1 the first L1 and the 
    """
    items = {}  # {itemset: count}
    itemsets = {}
    for transaction in transactions:
        for item in transaction:
            items[item] = items.get(item, 0) + 1
            
    L1 = []
    for k, v in items.iteritems():
        if v >= MIN_SUP * len(transactions):
            L1.append([k])
            itemsets[(k+"",)] = v;
    return L1, itemsets         

def get_transactions():
    """
    get transactions from file
    :return list of transactions
    """
    transactions = []
    
    with open(FILE_NAME, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            transactions.append(set(row[0].split(',')))
    return transactions


def main():
    # read_parameters()
    trans = get_transactions()
    itemsets, rules = apriori(trans)

    n = len(trans)
    print "==Frequent itemsets (min_sup=" + str(MIN_SUP * 100) + "%)"
    for k,v in itemsets.iteritems():
        print k,
        print str(v * 100 / n) + "%"
    print "==High-confidence association rules (min_conf=" + str(MIN_CONF*100) + "%)"
    for k, v in rules.iteritems():
        print k[0],
        print " => ",
        print k[1],
        print "(Conf: "+ str(v*100) + "%, Supp:" + str(itemsets[k[0]] * 100 / n) + "%)"

if __name__ == '__main__':
	main()