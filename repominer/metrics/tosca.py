from io import StringIO
from toscametrics import metrics_extractor
from .base import BaseMetricsExtractor
from repominer.filters import is_tosca_file


class ToscaMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str, at: str):
        super().__init__(path_to_repo, at)

    def get_product_metrics(self, script: str) -> dict:
        """
        Extract product metrics from a script
        """
        try:
            return metrics_extractor.extract_all(StringIO(script))
        except ValueError:
            return {}

    def ignore_file(self, path_to_file: str, content: str = None):
        return not is_tosca_file(path_to_file, content)
