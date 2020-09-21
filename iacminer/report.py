"""
This module is responsible to generate html reports for the mining
"""
import statistics
import datetime

from typing import List
from iacminer.file import LabeledFile

def create_report(labeled_files: List[LabeledFile]) -> str:
    """
    Generate an HTML report for the crawled repositories.
    :param labeled_files: a list of labeled files
    :return: the HTML report
    """
    return "HTML REPORT HERE"
