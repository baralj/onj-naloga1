from datetime import date, timedelta
from langdetect import detect
import os
import shutil
import wget
import gzip
import mailbox
import re
import unicodedata
import string

TAG_RE = re.compile('<.*?>')
WORD_RE = re.compile(r"""[^a-zA-Z\.\-!?,'"/]""")

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def download_spam():
    url_start = 'http://artinvoice.hu/spams/spam--'
    start_date = date(2018, 1, 1)
    end_date = date.today()
    for single_date in daterange(start_date, end_date):
        url_date = url_start + str(single_date) + ".gz"
        filename = wget.download(url_date, out='spam')
        with gzip.open(filename, 'rb') as f_in:
            with open(filename[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    extracted_files = os.listdir("spam")
    for f in extracted_files:
        if f.endswith(".gz"):
            absolute_path = os.path.abspath(os.path.join('spam', f))
            os.remove(absolute_path)


def getcharsets(msg):
    charsets = set({})
    for c in msg.get_charsets():
        if c is not None:
            charsets.update([c])
    return charsets


def getBody(msg):
    while msg.is_multipart():
        msg = msg.get_payload()[0]
    t = msg.get_payload(decode=True)
    for charset in getcharsets(msg):
        if charset == 'cp-850':
            charset = 'cp850'
        try:
            t = t.decode(charset)
        except:
            t = ""
    return t


download_spam()
spam = []
over = False
idx = 0
with open(os.path.join('valid_words', 'words_alpha.txt')) as word_file:
    valid_words = set(word_file.read().split())
for filename in os.listdir('spam'):
    if over:
        break
    mbox = mailbox.mbox(os.path.join('spam', filename))
    message_list = set()
    for message in mbox:
        if idx == 10000:
            over = True
            break
        message_tmp = []
        if isinstance(getBody(message), (bytes, bytearray)):
            message_dec = TAG_RE.sub('', str(getBody(message)))
        else:
            message_dec = TAG_RE.sub('', getBody(message))
        if not isinstance(message_dec, str):
            message_dec = unicodedata.normalize('NFKD', message_dec).encode('ascii', 'ignore')

        message_dec = message_dec.lower().translate(None, string.punctuation)

        # if not message_dec or len(message_dec.strip()) < 20:
        #     continue

        try:
            if not detect(message_dec) == "en":
                continue
        except:
            continue

        for item in message_dec.split():
            if not WORD_RE.search(item):
                if item in valid_words:
                    message_tmp.append(item)

        if " ".join(message_tmp) in message_list or not message_tmp or len(" ".join(message_tmp).strip()) < 10:
            continue

        message_list.add(" ".join(message_tmp))
        spam.append(" ".join(message_tmp))
        idx += 1

for idx, txt in enumerate(spam):
    f = open(os.path.join('corpus_spam', "spam_%05d.txt" % idx), 'w')
    f.write(txt.encode('utf-8').strip())
    f.close()