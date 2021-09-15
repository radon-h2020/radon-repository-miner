from .base import BaseMetricsExtractor
from repominer.filters import is_tosca_file
from toscametrics.import_metrics import general_metrics, blueprint_metrics

METRICS_TO_COMPUTE = (
    'lines_code',
    'lines_blank',
    'num_keys',
    'num_suspicious_comments',
    'num_tokens',
    'text_entropy',
    'num_imports',
    'num_inputs',
    'num_interfaces',
    'num_node_templates',
    'num_node_types',
    'num_parameters',
    'num_properties',
    'num_relationship_templates',
    'num_relationship_types',
    'num_shell_scripts'
)


class ToscaMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str, clone_repo_to: str = None, at: str = 'release'):
        super().__init__(path_to_repo, clone_repo_to, at)

    def get_product_metrics(self, script: str) -> dict:
        """ Extract source code metrics from a script.
        It uses ToscaMetrics to compute the metrics (https://github.com/radon-h2020/radon-tosca-metrics)

        Parameters
        ----------
        script : str
            The content of the script to extract metrics from.

        Returns
        -------
        Dict[str, Any]
            A dictionary of <metric, value>.

        """
        results = {}

        metrics = general_metrics
        metrics.update(blueprint_metrics)

        for name in metrics:

            if name not in METRICS_TO_COMPUTE:
                continue

            try:
                results[name] = metrics[name](script).count()
            except TypeError:
                continue

        return results

    def ignore_file(self, path_to_file: str, content: str = None):
        return not is_tosca_file(path_to_file, content)
