import nltk
import re


def Emission(Bank, TagBank, line):
    tokens = nltk.word_tokenize(line)

    if tokens[3] in TagBank:
        TagBank[tokens[3]] += 1
    else:
        TagBank[tokens[3]] = 1

    if tokens[1] in Bank:
        if tokens[3] in Bank[tokens[1]]:
            Bank[tokens[1]][tokens[3]] += 1
        else:
            Bank[tokens[1]][tokens[3]] = 1
    else:
        Bank[tokens[1]] = {}
        Bank[tokens[1]][tokens[3]] = 1


def Transition(Bank, line, pline):
    tokens = nltk.word_tokenize(line)
    ptokens = nltk.word_tokenize(pline)
    if ptokens[3] in Bank:
        if tokens[3] in Bank[ptokens[3]]:
            Bank[ptokens[3]][tokens[3]] += 1
        else:
            Bank[ptokens[3]][tokens[3]] = 1
    else:
        Bank[ptokens[3]] = {}
        Bank[ptokens[3]][tokens[3]] = 1


def Start(ETable, TTable, TagBank, file, Tester, Answer):
    file = open(file, 'r')
    start = '0	0Start0	_	START	_	_	_	_	_	_'
    stop = '0	0Stop0	_	STOP	_	_	_	_	_	_'

    train_counter = 0
    test_counter = 0
    line = file.readline()

    while line:
        pline = line
        line = file.readline()
        loweredLine = line.lower()
        loweredPLine = pline.lower()

        if line:
            if (line == '\n'):
                train_counter += 1
                if (train_counter >= 90):
                    break
            elif (line[:1] != '#'):
                Emission(ETable, TagBank, loweredLine)
                if (float(line[:2]) == 1):
                    Transition(TTable, loweredLine, start)
                else:
                    Transition(TTable, loweredLine, loweredPLine)

    tags = []
    while line:
        line = file.readline()
        loweredLine = line.lower()

        if '# text = ' in line:
            s = re.sub('# text = ', '', loweredLine)
            Tester.append(s)
        if (line == '\n'):
            test_counter += 1
            if (test_counter >= 10):
                break
            Answer.append(tags)
            tags = []
        elif line[:1] != '#':
            tokens = nltk.word_tokenize(loweredLine)
            tags.append(tokens[3])

#Probability Table Builder
def DoEmissionTable(ETable,TagBank):
    for words in ETable:
        for tag in ETable[words]:
            ETable[words][tag] = ETable[words][tag] / TagBank[tag]

def DoTransitionTable(TTable,TagBank):
    for ptag in TTable:
        for tag in TTable[ptag]:
            TTable[ptag][tag] = TTable[ptag][tag] / TagBank[ptag]

#Unknown Word Handling for Number
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#POSTagger
def EmissionPOSTagger(ETable, Tester, Result):
    for sentence in Tester:
        tokens = nltk.word_tokenize(sentence)
        tagged = []
        for token in tokens:
            if token in ETable:
                maxValue = max(ETable[token].values())
                tag = max(ETable[token].keys(), key=(lambda k: ETable[token][k]))
                tagged.append(tag)
            else:
                if isNumber(token):
                    tagged.append('num')
                else:
                    tagged.append('verb')
        Result.append(tagged)

def ViterbiPOSTagger(ETable, TTable, TagBank, Tester, Result):
    for sentence in Tester:
        tokens = nltk.word_tokenize(sentence)
        tagged = []
        ptag = 'START'
        ctag = ''
        SProb = 1

        for token in tokens:
            MaxProb = 0

            if token not in ETable:
                if isNumber(token):
                    ctag = 'num'
                    if ctag in TTable[ptag]:
                        MaxProb = SProb * 1 * TTable[ptag][ctag]
                    else:
                        MaxProb = 1

                else:
                    ctag = 'verb'
                    if ctag in TTable[ptag]:
                        MaxProb = SProb * 1 * TTable[ptag][ctag]
                    else:
                        MaxProb = 1
            else:
                for tag in ETable[token]:
                    if tag not in TTable[ptag]:
                        ETable[token][tag] += 1
                        TTable[ptag][tag] = 1
                        DoEmissionTable(ETable, TagBank)
                        DoTransitionTable(TTable, TagBank)

                    p = SProb * ETable[token][tag] * TTable[ptag][tag]
                    if (p > MaxProb):
                        MaxProb = p
                        ctag = tag

            SProb = MaxProb
            tagged.append(ctag)
            ptag = ctag
        Result.append(tagged)

#Evaluator
def Evaluate(Answer, Result):
    Correct = 0
    Total   = 0

    for i in range(0, len(Answer)):
        for j in range(0, len(Answer[i])):
            Total += 1
            if (Answer[i][j] == Result[i][j]):
                Correct += 1

    print (Correct / Total)

