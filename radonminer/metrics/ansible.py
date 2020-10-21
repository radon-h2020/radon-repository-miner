import io

from ansiblemetrics import metrics_extractor
from .base import BaseMetricsExtractor


class AnsibleMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str):
        super().__init__(path_to_repo)

    def get_product_metrics(self, script: str) -> dict:
        """
        Extract product metrics from a script
        """
        try:
            return metrics_extractor.extract_all(io.StringIO(script))
        except ValueError:
            return {}
