import re
import spacy
from typing import List

nlp = spacy.load("en_core_web_sm")


def get_head_dependents(sentence: str) -> List[str]:
    """
    Compute the syntactic dependencies and
    return a list of tuples (head, dependents)

    Parameters
    ----------
    sentence : str
        The sentence to analyze

    Return
    ------
    str
        A list of tuples (head, dependents).

    """
    sentence = re.sub(r'\s+', ' ', sentence)
    doc = nlp(sentence)
    dep = [token.dep_ for token in doc]

    # Get list of compounds in doc
    compounds = [token for token in doc if token.dep_ == 'compound']

    # Identifies roots and direct objects
    for token in compounds:
        if token.head.dep_ == 'dobj':
            dep[token.i] = 'dobj'
        elif token.head.dep_ == 'ROOT':
            dep[token.i] = 'ROOT'

    return [token.text for token in doc if dep[token.i] in ('ROOT', 'dobj')]


def key_value_list(d):
    """
    This function iterates over all the key-value pairs of a dictionary and
    returns a list of tuples (key, value).

    Parameters
    ----------
    d : Union[dict, list]
        The dictionary to iterate through

    Return
    ------
    str
        A list of tuples (key, value).

    """
    if not isinstance(d, dict) and not isinstance(d, list):
        return []

    key_values = []

    if isinstance(d, list):
        for entry in d:
            if isinstance(entry, dict):
                key_values.extend(key_value_list(entry))
    else:
        for k, v in d.items():
            if k is None or v is None:
                continue

            key_values.append((k, v))
            key_values.extend(key_value_list(v))

    return key_values
