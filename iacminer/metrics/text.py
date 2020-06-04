import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

REGEX_BOOLEAN = re.compile(r'^(true|false)$')
REGEX_HASH = re.compile(r'^[a-f0-9]{32, 64}$')
REGEX_EMAIL = re.compile(r"\b[^\s]+@[^\s]+[.][^\s]+\b")
REGEX_PATH = re.compile(r'^.*\.([^\d]+\d*)+')
REGEX_URL = re.compile(r'(http|https)://[^\s]*')


class TextProcessing:

    def __init__(self, text: str):
        self.text = text
        self.stopwords = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def process(self):
        tokens = []

        for line in self.text.splitlines():
            # Remove comments
            line = re.sub(r'#.*', '', line)

            # Tokenize
            for token in nltk.word_tokenize(line):
                # Split snake case
                for word in token.split('_'):
                    # Split camel case, if any
                    tokens.extend(self.camel_case_split(word))

        # To lower case
        tokens = [t.lower().strip() for t in tokens]

        # Remove booleans
        tokens = [REGEX_BOOLEAN.sub('', t) for t in tokens]

        # Replace emails with 'email'
        tokens = [REGEX_EMAIL.sub('email', t) for t in tokens]

        # Replace hashes with 'hash'
        tokens = [REGEX_HASH.sub('hash', t) for t in tokens]

        # Replace paths with 'path'
        tokens = [REGEX_PATH.sub('path', t) for t in tokens]

        # Replace urls with 'url'
        tokens = [REGEX_URL.sub('url', t) for t in tokens]

        # Remove any non-word character and digit
        tokens = [re.sub(r'[\W\d]', '', t) for t in tokens]

        # Remove tokens consisting of less than 3 characters
        tokens = [t for t in tokens if len(t.strip()) > 2]

        # Remove stop words
        tokens = [t for t in tokens if t not in self.stopwords]

        # Apply porter stemming
        tokens = [self.stemmer.stem(t) for t in tokens]

        return tokens

    @staticmethod
    def camel_case_split(token):

        if not token:
            return ''

        words = [[token[0]]]

        for c in token[1:]:
            if words[-1][-1].islower() and c.isupper():
                words.append(list(c))
            else:
                words[-1].append(c)

        return [''.join(word) for word in words]
