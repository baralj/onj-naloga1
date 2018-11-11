import nltk
import sklearn
from sklearn.naive_bayes import MultinomialNB
import os


corpus_ham = nltk.corpus.PlaintextCorpusReader('corpus_ham', '.*')
corpus_spam = nltk.corpus.PlaintextCorpusReader('corpus_spam', '.*')

stop_words = set(nltk.corpus.stopwords.words("english"))
typical_words = ['dear', 'hi', 'best', 'regards', 'sir', 'madam']
filt_messages = []
messages = []
is_spam = []

stemmer = nltk.stem.SnowballStemmer("english")

for idx in corpus_ham.fileids():
    sent = []
    for word in corpus_ham.words(idx):
        if word not in stop_words and word not in typical_words:
            sent.append(stemmer.stem(word))
    if sent:
        messages.append(corpus_ham.words(idx))
        filt_messages.append(" ".join(sent))
        is_spam.append(0)


for idx in corpus_spam.fileids():
    sent = []
    for word in corpus_spam.words(idx):
        if word not in stop_words and word not in typical_words:
            sent.append(stemmer.stem(word))
    if sent:
        filt_messages.append(" ".join(sent))
        is_spam.append(1)

data_train, data_test, y_train, y_test = sklearn.model_selection.train_test_split(filt_messages, is_spam, test_size=0.2, shuffle=True)
tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer()

X_train = tfidf_vectorizer.fit_transform(data_train)
X_test = tfidf_vectorizer.transform(data_test)

clf = MultinomialNB(alpha=.01)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

score = sklearn.metrics.accuracy_score(y_test, pred)
print("Classification accuracy:   %0.3f" % score)

print("Precision:  %0.3f" % sklearn.metrics.precision_score(y_test, pred))
print("Recall:  %0.3f" % sklearn.metrics.recall_score(y_test, pred))
print("F-Score:  %0.3f" % sklearn.metrics.f1_score(y_test, pred))

sklearn.externals.joblib.dump(tfidf_vectorizer,  os.path.join('model', 'tfidf_vectorizer.pkl'))
sklearn.externals.joblib.dump(clf,  os.path.join('model', 'classify_spam.pkl'))