from functools import wraps
from flask import Flask, request, Response, render_template
import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import math
from collections import Counter
import sys
import os

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.feature_extraction.text")


app = Flask(__name__)

def entropy(s):
    p, lns = Counter(s), float(len(s))
    return -sum(count/lns * math.log(count/lns, 2) for count in p.values())

def getTokens(input):
    tokensBySlash = str(input).split('/')
    allTokens = []
    for i in tokensBySlash:
        tokens = str(i).split('-')
        tokensByDot = []
        for j in range(len(tokens)):
            tempTokens = str(tokens[j]).split('.')
            tokensByDot = tokensByDot + tempTokens
        allTokens = allTokens + tokens + tokensByDot
    allTokens = list(set(allTokens))
    if 'com' in allTokens:
        allTokens.remove('com')
    return allTokens




def TL():
    allurls = './data/dataset.csv'

    df = pd.read_csv(
        allurls,
        delimiter=',',
        on_bad_lines='skip',
        na_filter=False
    )

    # Make sure columns exist: '', 'url', 'label', 'result'
    # Drop the first unnamed index column
    if df.columns[0].startswith('Unnamed') or df.columns[0] == '':
        df = df.iloc[:, 1:]

    # Now df columns should be: url, label, result
    df = df[['url', 'label']].dropna()

    # Optional: sample to reduce memory
    df = df.sample(n=min(5000, len(df)), random_state=42)

    corpus = df['url'].astype(str).tolist()
    y = df['label'].astype(str).tolist()

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier
    from sklearn.model_selection import train_test_split

    vectorizer = TfidfVectorizer(
        tokenizer=getTokens,
        lowercase=False,
        max_features=10000,
        min_df=2
    )
    X = vectorizer.fit_transform(corpus)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = SGDClassifier()
    model.fit(X_train, y_train)
    print("Accuracy:", model.score(X_test, y_test))
    return vectorizer, model


@app.route('/<path:path>')
def show_index(path):
    X_predict = vectorizer.transform([str(path)])
    y_pred = lgs.predict(X_predict)[0]    # e.g. "Good" or "Bad"

    if y_pred.lower() in ["good", "benign", "legit"]:
        result = "Good"
    else:
        result = "malicious"

    return f"""
You asked for : <h1>{path}</h1><br>

AI output: {result}<br>

Entropy: {entropy(path)}
"""



port = os.getenv('VCAP_APP_PORT', 5000)
if __name__ == "__main__":
    vectorizer, lgs = TL()
    app.run(host='0.0.0.0', port=int(port), debug=True)
