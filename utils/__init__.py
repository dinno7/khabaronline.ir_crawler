import re

from hazm import Normalizer, Stemmer, WordTokenizer, stopwords_list

normalizer = Normalizer()
stemmer = Stemmer()
tokenizer = WordTokenizer()
stop_words = set(stopwords_list() + ["و", "در", "به"])


def remove_special_chars(text):
    text = re.sub(r"[^\w\s]", "", text)
    return text


def to_lowercase(text):
    return text.lower()


def tokenize_fa(text):
    tokenizer = WordTokenizer()
    tokens = tokenizer.tokenize(text)
    return tokens


def stem_fa(text):
    stemmer = Stemmer()
    tokens = tokenize_fa(text)
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return " ".join(stemmed_tokens)


def remove_stopwords_fa(text):
    stop_words = set(stopwords_list())
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return " ".join(filtered_tokens)


def preprocess_text_fa(text):
    text = remove_special_chars(text)
    text = to_lowercase(text)
    text = remove_stopwords_fa(text)
    text = stem_fa(text)
    return text
