from .base import BaseMetricsExtractor


class ToscaMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str):
        super().__init__(path_to_repo)

    def get_product_metrics(self, script: str) -> dict:
        """
        Extract product metrics from a script
        """
        raise NotImplementedError
