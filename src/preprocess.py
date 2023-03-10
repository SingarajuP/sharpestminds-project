""" preprocessing for prediction"""
import re
import time
from string import punctuation
from bs4 import BeautifulSoup
import requests
import pandas as pd
import nltk
import nltk.data
from nltk.stem import WordNetLemmatizer
from src.config import BASE_URL, BOOK_URL
from src.utils import tokenizer


def get_reviews(title):
    """getting reviews from the book title as a dataframe"""

    data = {"q": title}
    GOODREADS_URL = BOOK_URL
    start_time = time.time()
    req = requests.get(GOODREADS_URL, params=data, timeout=60)
    request_time = time.time() - start_time
    print(
        "Time to get response for book title search from goodreads is :", request_time
    )
    book_soup = BeautifulSoup(req.text, "html.parser")

    titles = book_soup.find_all("a", class_="bookTitle")
    title = []
    link = []
    for bookname in titles:
        title.append(bookname.get_text())
        link.append(bookname["href"])
    rev = BASE_URL + link[0]
    start_time = time.time()
    rev_url = requests.get(rev, timeout=60)
    request_time = time.time() - start_time
    print("Time to get response for reviews:", request_time)
    rev_soup = BeautifulSoup(rev_url.content, "html.parser")
    rev_list = []
    for x in rev_soup.find_all("section", {"class": "ReviewText"}):
        rev_list.append(x.text)
    df = pd.DataFrame(rev_list, columns=["reviews"])
    return df


def text_cleaning(text):
    """This function will change the text to lower case, remove tags,
    special characters,digits, punctuation and lemmatization"""

    text = re.sub(r"\(.*?\)", "", text)

    text = re.sub(r"[^A-Za-z]", " ", str(text))

    text = re.sub(r"&lt;/?.*?&gt;", " &lt;&gt; ", text)
    text = re.sub(r"(\\d|\\W)+", " ", text)
    text = "".join([c for c in text if c not in punctuation])
    stopwords = nltk.corpus.stopwords.words("english")
    text = text.split()
    text = [w for w in text if not w in stopwords]
    text = " ".join(text)

    text = text.split()
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in text]
    text = " ".join(lemmatized_words)
    text = text.lower()
    return text


def tokenize_data(example):
    """This function returns the tokenized vectors for bert model"""

    return tokenizer(example["reviews"], truncation=True, padding="max_length")
