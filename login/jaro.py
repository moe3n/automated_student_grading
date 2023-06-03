from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import spacy
import numpy as np


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
    # Join the modified words not not_back not_into a single string and return it
    return " ".join(words)


def preprocess(s1, s2):
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
    punctuation_pattern = r'[^\w\s]'
    s1 = re.sub(punctuation_pattern, '', s1)
    s2 = re.sub(punctuation_pattern, '', s2)
    return s1, s2


def jaro_winkler(str1: str, str2: str) -> float:

    def get_matched_characters(_str1: str, _str2: str) -> str:
        matched = []
        limit = min(len(_str1), len(_str2)) // 2
        for i, l in enumerate(_str1):
            left = int(max(0, i - limit))
            right = int(min(i + limit + 1, len(_str2)))
            if l in _str2[left:right]:
                matched.append(l)
                _str2 = f"{_str2[0:_str2.index(l)]} {_str2[_str2.index(l) + 1:]}"

        return "".join(matched)

    # matching characters
    matching_1 = get_matched_characters(str1, str2)
    matching_2 = get_matched_characters(str2, str1)
    match_count = len(matching_1)

    # transposition
    transpositions = (
        len([(c1, c2) for c1, c2 in zip(matching_1, matching_2) if c1 != c2]) // 2
    )

    if not match_count:
        jaro = 0.0
    else:
        jaro = (
            1
            / 3
            * (
                match_count / len(str1)
                + match_count / len(str2)
                + (match_count - transpositions) / match_count
            )
        )

    # common prefix up to 4 characters
    prefix_len = 0
    for c1, c2 in zip(str1[:4], str2[:4]):
        if c1 == c2:
            prefix_len += 1
        else:
            break

    return jaro + 0.1 * prefix_len * (1 - jaro)


def combined_similarity(s1, s2, p=0.1):
    # Compute the Jaro-Winkler similarity
    s1, s2 = preprocess(s1, s2)
    jaro_winkler_sim = jaro_winkler(s1, s2)

    # Compute the TF-IDF cosine similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([s1, s2])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    jaro_winkler_sim_norm = jaro_winkler_sim / 1.0
    cosine_sim_norm = (cosine_sim + 1.0) / 2.0
    print("cosine sim:", cosine_sim)
    print("jw:", jaro_winkler_sim_norm)

    # Combine the Jaro-Winkler and cosine similarities using a weighted average
    alpha = .5  # Adjust this value to change the weight of the Jaro-Winkler similarity
    combined_sim = alpha * jaro_winkler_sim + (1 - alpha) * cosine_sim

    return jaro_winkler_sim_norm
