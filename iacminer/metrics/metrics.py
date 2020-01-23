import os
import pandas as pd
import yaml

from io import StringIO

import pydriller
#import pydriller.metrics.process.metrics as process_metrics

from ansiblemetrics.main import MetricExtractor, LoadingError

class Metrics():

    def __init__(self):
        self.__extractor = MetricExtractor()


    def __calculate(self, script, path_to_repo, filepath, commit_sha):
        """
        try:
            metrics = self.__extractor.run(script)

            metrics['comm'] = process_metrics.commits_count
            
            devs_count = process_metrics.devs_count(path_to_repo, filepath, to_commit=commit_sha)
            metrics['ddev'] = devs_count[0]
            metrics['adev'] = devs_count[1]

            devs_exp = process_metrics.devs_experience
            metrics['own'] = devs_exp[0]
            metrics['oexp'] = devs_exp[1]
            metrics['exp'] = devs_exp[2]

            hcm = process_metrics.history_complexity
            metrics['hcm_c1'] = hcm[0]
            metrics['hcm_cp'] = hcm[1]
            metrics['hcm_cu'] = hcm[2]

            metrics['hunk'] = process_metrics.hunks_count
            metrics['minor'] = process_metrics.minor_contributors_count
            metrics['new_devs'] = process_metrics.news_devs_count
            
            norm_lines = process_metrics.norm_lines_count
            metrics['add'] = norm_lines[0]
            metrics['del'] = norm_lines[1]

            return metrics

        except LoadingError:
                print('\033[91m' + 'Error: failed to load {}. Insert a valid file!'.format('FILENAME HERE') + '\033[0m')
        except yaml.YAMLError:
                print('The input file is not a yaml file')
        except Exception:
                print('An unknown error has occurred')
        finally:
            return None
        """


    def calculate(self, defective_scripts, unclassified_scripts):
            """
            metrics_list = []
            for content in defective_scripts:
                path_to_repo = f'https://github.com/{content.repository}'
                
                metrics = self.__calculate(StringIO(content.decoded_content), 
                                           path_to_repo,
                                           content.filename,
                                           commit_sha)
                
                if metrics:
                    metrics['filepath'] = content.filename
                    metrics['sha'] = content.sha
                    metrics['repository'] = content.repository
                    metrics['defective'] = 'yes'
                    metrics_list.append(metrics)
            
            for content in unclassified_scripts:
                metrics = self.__calculate(content)
                if metrics:
                    metrics['defective'] = 'no'
                    metrics_list.append(metrics)

            dataset = pd.DataFrame(metrics_list)
            with open(os.path.join('data', 'metrics.csv'), 'w') as out:
                dataset.to_csv(out, mode='w', index=False)

            return dataset
            """
            return None
