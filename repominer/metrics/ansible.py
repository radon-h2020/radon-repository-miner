from ansiblemetrics.import_metrics import general_metrics, playbook_metrics

from .base import BaseMetricsExtractor
from repominer.filters import is_ansible_file

METRICS_TO_COMPUTE = (
    'lines_code',
    'lines_blank',
    'num_conditions',
    'num_keys',
    'num_tokens',
    'text_entropy',
    'avg_play_size',
    'num_distinct_modules',
    'num_parameters',
    'num_tasks',
    'num_unique_names'
)


class AnsibleMetricsExtractor(BaseMetricsExtractor):

    def __init__(self, path_to_repo: str, clone_repo_to: str = None, at: str = 'release'):
        super().__init__(path_to_repo, clone_repo_to, at)

    def get_product_metrics(self, script: str) -> dict:
        """ Extract source code metrics from a script.
        It uses AnsibleMetrics to compute the metrics (https://github.com/radon-h2020/radon-ansible-metrics)

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
        metrics.update(playbook_metrics)

        for name in metrics:

            if name not in METRICS_TO_COMPUTE:
                continue

            try:
                results[name] = metrics[name](script).count()
            except TypeError:
                continue

        return results

    def ignore_file(self, path_to_file: str, content: str = None):
        return not is_ansible_file(path_to_file)
