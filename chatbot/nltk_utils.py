import nltk
import numpy as np
# nltk.download('punkt_tab')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
# Ensure punkt tokenizer is available; fallback gracefully
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except Exception:
        pass

def tokenize(sentence):
    try:
        return nltk.word_tokenize(sentence)
    except LookupError:
        # Fallback: simple whitespace split if punkt unavailable
        return sentence.split()


def stem(words):
    return stemmer.stem(words.lower())


def bag_of_words(tokenize_sentence, all_words):
    tokenize_sentence = [stem(w) for w in tokenize_sentence]

    bag = np.zeros(len(all_words), dtype = np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenize_sentence:
            bag[idx] = 1.0

    return bag 

# sentence = ["hello", "how", "are", "you"]
# words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
# bag = bag_of_words(sentence, words)
# print(bag)





