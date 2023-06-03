import re
import spacy
import numpy as np
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import string
from scipy.spatial import distance


def lemmatize(sentence):
    # Load the English language model
    nlp = spacy.load("en_core_web_sm")

    ar = nlp.get_pipe("attribute_ruler")

    ar.add([[{'TEXT': 'bruh'}], [{'TEXT': 'bruv'}], [
           {'TEXT': 'bro'}], [{'TEXT': 'broh'}]], {'LEMMA': 'Brother'})

    # Example sentence
    # sentence = "bruv playing each other ball talkative cat slower abode worn"

    # Process the sentence by the lemmatizer
    doc = nlp(sentence)

    # Get the lemmatized tokens
    lemmatized_words = [token.lemma_ for token in doc]

    # Print the lemmatized words
    # print('lemmatized',lemmatized_words)
    return lemmatized_words


def negate_sequence(text):
    # Define a list of negation words and phrases
    negations = ["not", "no", "never", "nothing", "nowhere", "neither", "nor", "non-" "can't", "won't", "shouldn't", "wouldn't", "doesn't", "isn't", "aren't", "ain't", "haven't", "hadn't",
                 "hasn't", "mustn't", "shan't", "wasn't", "weren't", "don't", "didn't", "couldn't", "mightn't", "needn't", "oughtn't", "hadn't've", "couldn't've", "shouldn't've", "wouldn't've"]
    # Split the input text into individual words
    words = text.split()
    # Initialize a flag variable to track whether the current word is negated or not
    negated = False
    # Iterate over each word in the list
    for i, word in enumerate(words):
        # Check if the current word is a negation word
        if word.lower() in negations:
            # If it is, set the negated flag to True
            negated = True
            print("negation found")
        # Otherwise, check if the previous word was negated and the current word is not a punctuation mark
        elif negated and not re.match(r'[^\w\s]', word):
            # If so, append a "not_" prefix to the current word and replace it in the list
            words[i] = "not_" + word
        # Reset the negated flag if the current word is a punctuation mark
        if re.match(r'[^\w\s]', word):
            negated = False
    # Join the modified words back into a single string and return it
    return " ".join(words)


def tokenization(s1, s2):
    tokens1 = word_tokenize(s1.lower())
    tokens2 = word_tokenize(s2.lower())
    s1 = [token for token in tokens1 if token not in string.punctuation]
    s1 = [token for token in tokens2 if token not in string.punctuation]
    # punctuation_pattern = r'[^\w\s]'
    # s1 = re.sub(punctuation_pattern, '', tokens1)
    # s2 = re.sub(punctuation_pattern, '', tokens2)
    stop_words = set(stopwords.words('english'))
    s1 = [token for token in s1 if token not in stop_words]
    s2 = [token for token in s2 if token not in stop_words]
    s1 = ' '.join(s1)
    s2 = ' '.join(s2)
    return s1, s2


def preprocess(s1, s2):

    s1, s2 = tokenization(s1, s2)
    s1 = lemmatize(s1)
    s2 = lemmatize(s2)
    s1 = ' '.join(s1)
    s2 = ' '.join(s2)
    # print('lemmatized',s1)
    # print('lemmatized s2',s2)
    s1 = negate_sequence(s1)
    s2 = negate_sequence(s2)

    # print('negate',s1)
    # print('negate s2',s2)

    return s1, s2


def levenshtein_similarity(s1, s2):
    # Preprocess the input strings by applying negation handling

    # Calculate the Levenshtein distance between the two input strings
    n = len(s1)
    m = len(s2)
    if n == 0:
        return 0.0
    if m == 0:
        return 0.0
    # init matrix to store distances
    d = [[0 for j in range(m+1)] for i in range(n+1)]
    # init the first row and column with 1,2,3,4.... for dynamic approach, 2*2 matrix min of the 3,
    # we start calculating from topmost left
    for i in range(1, n+1):  # column
        d[i][0] = i
    for j in range(1, m+1):  # row
        d[0][j] = j
    # Compute the Levenshtein distance
    for j in range(1, m+1):
        for i in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                cost = 0  # same characters, no cost
            else:
                cost = 1  # diferent characters, edit needed
            d[i][j] = min(d[i-1][j] + 1,          # deletion
                          d[i][j-1] + 1,          # insertion
                          d[i-1][j-1] + cost)     # substitution

    # Calculate the Levenshtein similarity score
    distance = d[n][m]
    max_length = max(len(s1), len(s2))
    similarity = 1 - distance / max_length
    return similarity


if __name__ == "__main__":
    s1 = "Set of devices connected to each other over the physical medium is known as a computer network. For example the Internet."
    s2 = "Set of devices connected to  other each through the physical medium is known as a new network."
    s1, s2 = preprocess(s1, s2)
    score = levenshtein_similarity(s1, s2)
    print(score)
