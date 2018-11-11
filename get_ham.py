from langdetect import detect
import os
import wget
import tarfile
import shutil
import string
import re

WORD_RE = re.compile(r"""[^a-zA-Z\.\-!?,'"/]""")

def download_ham():
    # # url = 'https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz'
    # # filename = wget.download(url, out='ham')
    # filename = os.path.join('ham', 'enron_mail_20150507.tar.gz')
    # with tarfile.open(filename, 'r') as f_in:
    #     f_in.extractall(path='ham')

    extracted_files = os.listdir("ham")
    for f in extracted_files:
        if f.endswith(".tar.gz"):
            absolute_path = os.path.abspath(os.path.join('ham', f))
            os.remove(absolute_path)

download_ham()
idx = 0
ham = []
over = False
with open(os.path.join('valid_words', 'words_alpha.txt')) as word_file:
    valid_words = set(word_file.read().split())

for root, dirs, files in os.walk('ham'):
    if over:
        break
    for name in files:
        if idx == 10000:
            over = True
            break
        f = open(os.path.join(root, name), 'r')
        raw_message = f.read()
        lines = raw_message.split('\n')
        message_dec = ''
        message_tmp = []
        for line in raw_message.split('\n'):
            if ":" in line or line.startswith("-"):
                continue
            message_dec += line.strip()

        message_dec = message_dec.lower().translate(None, string.punctuation)
        try:
            if not detect(message_dec) == "en":
                continue
        except:
            continue

        for item in message_dec.split():
            if not WORD_RE.search(item):
                if item in valid_words:
                    message_tmp.append(item)

        if not message_tmp or len(" ".join(message_tmp).strip()) < 10:
            continue

        ham.append(" ".join(message_tmp))
        idx += 1

for idx, txt in enumerate(ham):
    f = open(os.path.join('corpus_ham', "ham_%05d.txt" % idx), 'w')
    f.write(txt.encode('utf-8').strip())
    f.close()
