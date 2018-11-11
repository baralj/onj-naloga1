from sklearn.externals import joblib
from langdetect import detect
import os
import nltk
import string
import re

WORD_RE = re.compile(r"""[^a-zA-Z\.\-!?,'"/]""")
new_message = raw_input('Enter email message:\n')
new_message = new_message.lower().translate(None, string.punctuation)

clf = joblib.load(os.path.join('model', 'classify_spam.pkl'))
tfidf_vectorizer = joblib.load(os.path.join('model', 'tfidf_vectorizer.pkl'))

stop_words = set(nltk.corpus.stopwords.words("english"))
typical_words = ['dear', 'hi', 'best', 'regards', 'sir', 'madam']
filt_message = []
stemmer = nltk.stem.SnowballStemmer("english")
with open(os.path.join('valid_words', 'words_alpha.txt')) as word_file:
    valid_words = set(word_file.read().split())

try:
    if not detect(new_message) == "en":
        print("Non-valid message.")
    else:
        for word in new_message.split():
            if not WORD_RE.search(word) and word in valid_words and word not in stop_words:
                filt_message.append(stemmer.stem(word))

        if not filt_message:
            print("Non-valid message.")
        else:
            X_pred = tfidf_vectorizer.transform([" ".join(filt_message)])
            pred = clf.predict(X_pred)
            if pred == 0:
                print("Message is ham.")
            else:
                print("Message is spam.")
except:
    print("Non-valid message.")
