"""
This module implements rules to detect fixing-commit categories related to IaC defects,
as defined in http://chrisparnin.me/pdf/GangOfEight.pdf.
"""
import re
import nltk
import spacy

from typing import Union, List, Set, Tuple
from pydriller.domain.commit import Commit


# Important: downloading resources for NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

nlp = spacy.load("en_core_web_sm")


def has_defect_pattern(text: str) -> bool:
    string_pattern = ['error', 'bug', 'fix', 'issu', 'mistake', 'incorrect', 'fault', 'defect', 'flaw']
    return any(word in text.lower() for word in string_pattern)


def has_conditional_pattern(text: str) -> bool:
    string_pattern = ['logic', 'condit', 'boolean']
    return any(word in text.lower() for word in string_pattern)


def has_storage_configuration_pattern(text: str) -> bool:
    string_pattern = ['sql', 'db', 'databas']
    return any(word in text.lower() for word in string_pattern)


def has_file_configuration_pattern(text: str) -> bool:
    string_pattern = ['file', 'permiss']
    return any(word in text.lower() for word in string_pattern)


def has_network_configuration_pattern(text: str) -> bool:
    string_pattern = ['network', 'ip', 'address', 'port', 'tcp', 'dhcp']
    return any(word in text.lower() for word in string_pattern)


def has_user_configuration_pattern(text: str) -> bool:
    string_pattern = ['user', 'usernam', 'password']
    return any(word in text.lower() for word in string_pattern)


def has_cache_configuration_pattern(text: str) -> bool:
    return 'cach' in text.lower()


def has_dependency_pattern(text: str) -> bool:
    string_pattern = ['requir', 'depend', 'relat', 'order', 'sync', 'compat', 'ensur', 'inherit']
    return any(word in text.lower() for word in string_pattern)


def has_documentation_pattern(text: str) -> bool:
    string_pattern = ['doc', 'comment', 'spec', 'licens', 'copyright', 'notic', 'header', 'readm']
    return any(word in text.lower() for word in string_pattern)


def has_idempotency_pattern(text: str) -> bool:
    return 'idempot' in text.lower()


def has_security_pattern(text: str) -> bool:
    string_pattern = ['vul', 'ssl', 'secr', 'authent', 'password', 'secur', 'cve']
    return any(word in text.lower() for word in string_pattern)


def has_service_pattern(text: str) -> bool:
    string_pattern = ['servic', 'server']
    return any(word in text.lower() for word in string_pattern)


def has_syntax_pattern(text: str) -> bool:
    string_pattern = ['compil', 'lint', 'warn', 'typo', 'spell', 'indent', 'regex', 'variabl', 'whitespac']
    return any(word in text.lower() for word in string_pattern)


def get_head_dependents(sentence: str) -> List[str]:
    """
    Compute the syntactic dependencies and return a list of tuples (head, dependents)
    """
    sentence = re.sub(r'\s+', ' ', sentence)
    doc = nlp(sentence)
    dep = [token.dep_ for token in doc]

    compounds = [token for token in doc if token.dep_ == 'compound']  # Get list of compounds in doc
    for token in compounds:
        if token.head.dep_ == 'dobj':
            dep[token.i] = 'dobj'
        elif token.head.dep_ == 'ROOT':
            dep[token.i] = 'ROOT'

    return [token.text for token in doc if dep[token.i] in ('ROOT', 'dobj')]


class FixingCommitCategorizer:

    def __init__(self, commit: Commit):

        if commit is None:
            raise TypeError('Expected a pydriller.domain.commit.Commit object, not None.')

        self.sentences = []  # will be list of tokens list

        porter = nltk.stem.porter.PorterStemmer()
        for sentence in nltk.sent_tokenize(commit.msg): #.lower()):
            # split into words
            tokens = nltk.tokenize.word_tokenize(sentence)

            # remove all tokens that are not alphabetic
            tokens = [word.strip() for word in tokens if word.isalpha()]

            # filter out stop words (do not, they are useful for dependency parsing)
            #tokens = [w for w in tokens if not w in set(nltk.corpus.stopwords.words('english'))]

            # stemming of words
            #tokens = [porter.stem(word) for word in tokens]

            self.sentences.append(tokens)

    def fixes_conditional(self):

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and has_conditional_pattern(sentence_dep):
                return True

        return False

    def fixes_configuration_data(self):

        is_data_changed = False  # data_changed(commit.diff) # TODO, or commit.added or removed lines for the modified files
        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))

            if has_defect_pattern(sentence) and \
                    (has_storage_configuration_pattern(sentence_dep)
                     or has_file_configuration_pattern(sentence_dep)
                     or has_network_configuration_pattern(sentence_dep)
                     or has_user_configuration_pattern(sentence_dep)
                     or has_cache_configuration_pattern(sentence_dep)
                     or is_data_changed):
                return True

        return False

    def fixes_dependency(self):

        is_include_changed = False  # include_changed(commit.diff) # TODO, or commit.added or removed lines for any modified file

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and (has_dependency_pattern(sentence_dep) or is_include_changed):
                return True

        return False

    def fixes_documentation(self):

        is_comment_changed = False  # comment_changed(commit.diff) # TODO, or commit.added or removed lines for any modified file

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and (has_documentation_pattern(sentence_dep) or is_comment_changed):
                return True

        return False

    def fixes_idempotency(self):

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and has_idempotency_pattern(sentence_dep):
                return True

        return False

    def fixes_security(self):

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and has_security_pattern(sentence_dep):
                return True

        return False

    def fixes_service(self):

        is_service_changed = False  # service_changed(commit.diff) # TODO, or commit.added or removed lines for any modified file

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and (has_service_pattern(sentence_dep) or is_service_changed):
                return True

        return False

    def fixes_syntax(self):

        for sentence in self.sentences:
            sentence = ' '.join(sentence)
            sentence_dep = ' '.join(get_head_dependents(sentence))
            if has_defect_pattern(sentence) and has_syntax_pattern(sentence_dep):
                return True

        return False
