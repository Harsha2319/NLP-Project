import spacy
from nltk.corpus import wordnet
from spacy.matcher import Matcher
import json
import sys


def text_retrieve(file_name):
    with open(file_name, 'r', encoding="utf8") as f:
        text = f.read()
    f.close()
    return text


def check_born(sent, nlp, d, words, lemma, NER, NER_words, POS, indir):
    trigger = ['born', 'found', 'create', 'start']
    #print(indir)
    #print(NER)
    flag = False
    if 'PERSON' in d.keys():
        if d['PERSON'] >= 1:
            flag = True
    if 'ORG' in d.keys():
        if d['ORG'] >= 1:
            flag = True
    if flag:
        for i in range(len(POS)):
            if POS[i] == 'VERB' and (words[i] in trigger or lemma[i] in trigger):
                #print(indir[words[i]])
                temp = {}
                for i in range(len(NER)):
                    #print("NER : ", NER[i])
                    if NER[i] == 'ORG' or NER[i] == 'PERSON':
                        #print("Ancesters : ",indir[NER_words[i]][1])
                        for a in indir[NER_words[i]][1]:
                            #print("lemma : ",a, nlp(a)[0].lemma_)
                            #print("Relation : ", indir[NER_words[i]][0])
                            if (a in trigger or nlp(a)[0].lemma_ in trigger) and indir[NER_words[i]][0] == 'nsubjpass' or indir[NER_words[i]][0] == 'dobj' or indir[NER_words[i]][0] == 'nsubj':
                                temp["1"] = NER_words[i]

                if 'DATE' in NER:
                    temp["2"] = NER_words[NER.index('DATE')]
                else:
                    temp["2"] = 'None'
                loc = ''
                for i in range(len(NER)):
                    if NER[i] == 'GPE':
                        loc = loc + ' ' + NER_words[i]
                if loc == '':
                    temp["3"] = 'None'
                else:
                    temp["3"] = loc
                print("born")
                print(sent)
                print(temp)
                return temp
    return []


def check_acquire(sent, nlp, d, words, lemma, NER, NER_words, POS, indir):
    trigger_buy = ['buy', 'acquire', 'acquisition']
    trigger_sell = ['sell']

    if 'ORG' in d.keys():
        if d['ORG'] >= 2:
            for i in range(len(POS)):
                if POS[i] == 'VERB':
                    trigger = ''
                    if (words[i] in trigger_buy or lemma[i] in trigger_buy):
                        trigger = 'buy'
                    if (words[i] in trigger_sell or lemma[i] in trigger_sell):
                        trigger = 'sell'
                    if trigger == '':
                        return []
                    temp = {}
                    org = [0] * 2
                    for i in range(len(NER)):
                        if NER[i] == 'ORG':
                            if trigger == 'buy':
                                for w in NER_words[i].split():
                                    for a in indir[w][1]:
                                        #print("Word : ", w)
                                        #print("lemma : ", a, nlp(a)[0].lemma_)
                                        #print("Relation : ", indir[w][0])
                                        if (a in trigger_buy or nlp(a)[0].lemma_ in trigger_buy):
                                            if indir[w][0] == 'nsubjpass' or indir[w][0] == 'nsubj':
                                                temp["1"] = NER_words[i]
                                            if indir[w][0] == 'dobj' or indir[w][0] == 'pobj':
                                                temp["2"] = NER_words[i]

                            if trigger == 'sell':
                                for w in NER_words[i].split():
                                    for a in indir[w][1]:
                                        #print("Word : ", w)
                                        #print("lemma : ", a, nlp(a)[0].lemma_)
                                        #print("Relation : ", indir[w][0])
                                        if (a in trigger_sell or nlp(a)[0].lemma_ in trigger_sell):
                                            if indir[w][0] == 'dobj' or indir[w][0] == 'pobj':
                                                org[0] = NER_words[i]
                                            if indir[w][0] == 'nsubjpass' or indir[w][0] == 'nsubj':
                                                org[1] = NER_words[i]
                                temp["1"] = org[0]
                                temp["2"] = org[1]

                    if 'DATE' in NER:
                        temp["3"] = NER_words[NER.index('DATE')]
                    else:
                        temp["3"] = 'None'
                    print("acquire")
                    print(sent)
                    print(temp)
                    return temp
    return []


def check_part(sent, nlp, d, words, lemma, NER, NER_words, POS, holonymList, synonyms):
    flag = False
    if 'GPE' in d.keys():
        if d['GPE'] >= 2:
            flag = 'GPE'
    if 'ORG' in d.keys():
        if d['ORG'] >= 2:
            flag = 'ORG'
    #print(d)
    #print(NER)
    #print(NER_words)
    if flag:
        temp = {}
        trigger = 'part of'
        if trigger in str(sent):
            for i in range(len(NER)):
                if NER[i] == 'ORG':
                    if "1" not in temp.keys():
                        temp["1"] = NER_words[i]
                    else:
                        temp["2"] = NER_words[i]
                        print("part")
                        print(sent)
                        print(temp)
                        return temp
            for i in range(len(NER)):
                if NER[i] == 'GPE':
                    if "1" not in temp.keys():
                        temp["1"] = NER_words[i]
                    else:
                        temp["2"] = NER_words[i]
                        print("part")
                        print(sent)
                        print(temp)
                        return temp

        matcher = Matcher(nlp.vocab)
        pattern = [{"POS": "PROPN"}, {"IS_PUNCT": True}, {"POS": "PROPN"}]
        matcher.add("Location", [pattern])

        matches = matcher(sent)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            span = sent[start:end]  # The matched span
            # print(match_id, string_id, start, end, span.text)
            span = span.text.split(',')
            word1 = span[0]
            word2 = span[1].strip()
            if NER[NER_words.index(word1)] == 'GPE' and NER[NER_words.index(word2)] == 'GPE':
                for w2 in synonyms[word2]:
                    if w2 in holonymList[word1]:
                        #print(word1, word2, w2)
                        temp["1"] = word1
                        temp["2"] = word2
                        print("part")
                        print(sent)
                        print(temp)
                        return temp
    return []


def IndirectDependency(doc):
    Indir = {}
    for token in doc:
        ancestors = []
        for ancestor in token.ancestors:
            ancestors.append(ancestor.text)
        Indir[token.text] = [token.dep_, ancestors]
    return Indir


def main():
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        print(sys.argv[0], " takes  1 or 2  arguments . Not ", len(sys.argv) - 1)
        print("Argument 1 is input file name. ")
        print("Argument 2 is a boolean input to print task1 results")
        print("Eg: Python Final.py test.txt True")
        sys.exit()
    file = sys.argv[1]
    if len(sys.argv) != 3:
        task1 = False
    else:
        task1 = sys.argv[2]
    print("Input file Name : ", file)
    if task1:
        print("Printing Task1 output")
    else:
        print("Task1 output will not be printed. If you want to see task1 output pass second argument as True")
    print()

    nlp = spacy.load('en_core_web_lg')
    raw_text = text_retrieve(file)
    doc = nlp(raw_text)

    template = []
    born_template = []
    acquire_template = []
    part_template = []

    for sent in doc.sents:
        words = []
        lemma = []
        POS = []
        Dep_head = []
        Dep = []
        hyper = {}
        hypo = {}
        holo = {}
        mero = {}
        syn = {}
        indir = IndirectDependency(sent)
        for token in sent:
            words.append(token.text)
            lemma.append(token.lemma_)
            POS.append(token.pos_)
            Dep_head.append(token.head.text)
            Dep.append(token.dep_)
            token_wn = token.text.replace(" ", "_")
            t_synset = wordnet.synsets(token_wn)
            synonyms = []
            hypernymList = []
            hyponymList = []
            holonymList = []
            meronymList = []
            for index, tempSynset in enumerate(t_synset):
                for l in tempSynset.lemmas():
                    synonyms.append(l.name())
                hypernyms = tempSynset.hypernyms()
                for l in hypernyms:
                    hypernymList.append(l.lemma_names()[0])
                hyponyms = tempSynset.hyponyms()
                for l in hyponyms:
                    hyponymList.append(l.lemma_names()[0])
                holonyms = tempSynset.part_holonyms()
                for l in holonyms:
                    holonymList.append(l.lemma_names()[0])
                meronyms = tempSynset.part_meronyms()
                for l in meronyms:
                    meronymList.append(l.lemma_names()[0])
            hyper[token.text] = hypernymList
            hypo[token.text] = hyponymList
            holo[token.text] = holonymList
            mero[token.text] = meronymList
            syn[token.text] = synonyms
            """
            if task1:
                print("Synonyms of ", token.text, "------>", synonyms)
                print("Hypernyms of ", token.text, "------>", hypernymList)
                print("Hyponyms of ", token.text, "------>", hyponymList)
                print("Holonyms of ", token.text, "------>", holonymList)
                print("Meronyms of ", token.text, "------>", meronymList)
            """
        if task1:
            print()
            print("Printing task1 features ")
            print()
            print("Sentence :", sent)
            print("Words : ", words)
            print("Lemma : ", lemma)
            print("POS Tag : ", POS)
            print("Dependency Head : ", Dep_head)
            print("Dependency Relation : ", Dep)
            print("Indirect Dependency - ancestors", indir)
            print("Synonyms : ", syn)
            print("Hypernyms : ", hyper)
            print("Hyponyms : ", hypo)
            print("Holonyms : ", holo)
            print("Meronyms : ", mero)

        NER = []
        NER_words = []
        for ent in sent.ents:
            NER_words.append(ent.text)
            NER.append(ent.label_)
        d = {}
        for i in NER:

            if i not in d.keys():
                d[i] = 1
            else:
                d[i] += 1
        # print(d)
        # print()
        if task1:
            print("Named Entities : ", NER_words)
            print("Named Entity Type : ", NER)
        print()

        print("TEMPLATE FILLING")
        print()
        b_temp = check_born(sent, nlp, d, words, lemma, NER, NER_words, POS, indir)
        if b_temp != []:
            temp = {}
            temp['Template'] = "BORN"
            temp['Sentence'] = [str(sent)]
            temp['Arguments'] = b_temp
            template.append(temp)
            born_template.append(b_temp)
        a_temp = check_acquire(sent, nlp, d, words, lemma, NER, NER_words, POS, indir)
        if a_temp != []:
            temp = {}
            temp['Template'] = "ACQUIRE"
            temp['Sentence'] = [str(sent)]
            temp['Arguments'] = a_temp
            template.append(temp)
            acquire_template.append(a_temp)
        p_temp = check_part(sent, nlp, d, words, lemma, NER, NER_words, POS, holo, syn)
        if p_temp != []:
            temp = {}
            temp['Template'] = "PART"
            temp['Sentence'] = [str(sent)]
            temp['Arguments'] = p_temp
            template.append(temp)
            part_template.append(p_temp)
    """
    print()
    print("BORN TEMPLATE")
    print(born_template)
    print()
    print("ACQUIRE TEMPLATE")
    print(acquire_template)
    print()
    print("PART TEMPLATE")
    print(part_template)
    print()

    print("FINAL JSON TEMPLATES")
    print(template)
    """

    with open('output.json', 'w') as fout:
        json.dump(template, fout, indent=4)

main()