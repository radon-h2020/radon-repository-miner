from .base import BaseMetricsExtractor
from radonminer.filters import is_tosca_file

class ToscaMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str):
        super().__init__(path_to_repo)

    def get_product_metrics(self, script: str) -> dict:
        """
        Extract product metrics from a script
        """
        raise NotImplementedError

    def ignore_file(self, path_to_file: str, content: str = None):
        return not is_tosca_file(path_to_file, content)
