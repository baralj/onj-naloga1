import nltk
import sklearn
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd

corpus_ham = nltk.corpus.PlaintextCorpusReader('corpus_ham', '.*')
corpus_spam = nltk.corpus.PlaintextCorpusReader('corpus_spam', '.*')

stop_words = set(nltk.corpus.stopwords.words("english"))
typical_words = ['dear', 'hi', 'best', 'regards', 'sir', 'madam']
filt_messages = []
messages = []
is_spam = []
stemmer = nltk.stem.SnowballStemmer("english")

all_words_ham = []
for idx in corpus_ham.fileids():
    sent = []
    for word in corpus_ham.words(idx):
        if word not in stop_words and word not in typical_words:
            sent.append(stemmer.stem(word))
            all_words_ham.append(word)

    if sent:
        messages.append(corpus_ham.words(idx))
        filt_messages.append(" ".join(sent))
        is_spam.append(0)

all_words_spam = []
for idx in corpus_spam.fileids():
    sent = []
    for word in corpus_spam.words(idx):
        if word not in stop_words and word not in typical_words:
            sent.append(stemmer.stem(word))
            all_words_spam.append(word)
    if sent:
        filt_messages.append(" ".join(sent))
        is_spam.append(1)

# Analyze common words
fdist = nltk.probability.FreqDist(all_words_ham)
f = plt.figure(1)
fdist.plot(30, cumulative=False)
f.show()

fdist = nltk.probability.FreqDist(all_words_spam)
g = plt.figure(1)
fdist.plot(30, cumulative=False)
g.show()

# Extract 10 % of dataset for cluster analysis
data_train, _, y_train, _ = sklearn.model_selection.train_test_split(filt_messages, is_spam, test_size=0.9, shuffle=True)
tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer()

X_train = tfidf_vectorizer.fit_transform(data_train)
dist = 1 - sklearn.metrics.pairwise.cosine_similarity(X_train)

km = KMeans(n_clusters=2)
km.fit(X_train)

clusters = km.labels_.tolist()

mds = sklearn.manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=1)

pos = mds.fit_transform(dist)
xs, ys = pos[:, 0], pos[:, 1]

cluster_colors = {0: '#1b9e77', 1: '#d95f02'}
orig_colors = {0: '#7570b3', 1: '#e7298a'}
cluster_names = {0: 'ham', 1: 'spam'}

count_same = 0
for i in xrange(len(clusters)):
    if clusters[i] == y_train[i]:
        count_same += 1

print("Percentage of correctly grouped messages: " + str(200.0 * count_same / (len(clusters) + len(y_train))))

df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=y_train))
groups = df.groupby('label')
groups2 = df.groupby('title')

fig, ax = plt.subplots(figsize=(17, 9))
ax.margins(0.05)

for name, group in groups2:
    ax.plot(group.x, group.y, marker='o', linestyle='', ms=5, color=orig_colors[name],
            label=cluster_names[name], mec='none')
    ax.set_aspect('auto')
    ax.tick_params( \
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')
    ax.tick_params( \
        axis='y',  # changes apply to the y-axis
        which='both',  # both major and minor ticks are affected
        left='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelleft='off')

ax.legend(numpoints=1)  # show legend with only 1 point
plt.show()

fig2, ax = plt.subplots(figsize=(17, 9))
ax.margins(0.05)
for name, group in groups:
    ax.plot(group.x, group.y, marker='o', linestyle='', ms=5, color=cluster_colors[name],
            label=cluster_names[name], mec='none')
    ax.set_aspect('auto')
    ax.tick_params( \
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')
    ax.tick_params( \
        axis='y',  # changes apply to the y-axis
        which='both',  # both major and minor ticks are affected
        left='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelleft='off')

ax.legend(numpoints=1)  # show legend with only 1 point
plt.show()