import io

from ansiblemetrics import metrics_extractor
from .base import BaseMetricsExtractor
from repominer.filters import is_ansible_file


class AnsibleMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str, at: str):
        super().__init__(path_to_repo, at)

    def get_product_metrics(self, script: str) -> dict:
        """
        Extract product metrics from a script.
        :param script: the script from which to run AnsibleMetrics on
        :return: a dictionary {string: float} with metrics. If an error occurs, return an empty dictionary
        """
        try:
            return metrics_extractor.extract_all(io.StringIO(script))
        except (TypeError, ValueError):
            return {}

    def ignore_file(self, path_to_file: str, content: str = None):
        return not is_ansible_file(path_to_file)
