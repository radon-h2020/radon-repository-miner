import os
import pandas as pd
import yaml

from io import StringIO

import pydriller.metrics.process.metrics as process_metrics

from ansiblemetrics.main import MetricExtractor, LoadingError

class Metrics():

    def __init__(self):
        self.__code_metrics_extractor = MetricExtractor()

    def calculate(self, defective_scripts: set, unclassified_scripts: set):
            metrics_list = []
            commits_content_map = {}

            for content in defective_scripts.union(unclassified_scripts):
                if content.commit_sha not in commits_content_map:
                    commits_content_map[content.commit_sha] = []
                
                commits_content_map[content.commit_sha].append((content, content in defective_scripts))

            for commit, contents_list in commits_content_map.items():
                path_to_repo = f'https://github.com/{contents_list[0][0].repository}'

                # Compute process metrics
                commits_count = process_metrics.commits_count(path_to_repo, from_commit=None, to_commit=commit)
                contributors_count = process_metrics.contributors_count(path_to_repo, from_commit=None, to_commit=commit)
                highest_contributors_experience = process_metrics.highest_contributors_experience(path_to_repo, from_commit=None, to_commit=commit)
                #pm = process_metrics.history_complexity(path_to_repo, periods=[('some_commit', 'other_commit')])
                hunks_count = process_metrics.hunks_count(path_to_repo, from_commit=commit, to_commit=commit)
                median_hunks_count = process_metrics.hunks_count(path_to_repo, from_commit=None, to_commit=commit)
                lines_count = process_metrics.lines_count(path_to_repo, from_commit=None, to_commit=commit)

                for content, defective in contents_list:
                    print(f'Extracting metrics from {content.repository}/commit/{commit}/{content.filename} [defective={defective}]')

                    filepath = content.filename

                    metrics = {}

                    # Storing metadata
                    metrics['filepath'] = filepath
                    metrics['file_sha'] = content.sha
                    metrics['commit_sha'] = content.commit_sha
                    metrics['repository'] = content.repository
                    metrics['defective'] = 'yes' if defective else 'no'

                    # Saving process metrics
                    metrics['commits_count'] = commits_count.get(filepath, 0)
                    metrics['contributors_count'] = contributors_count.get(filepath, {}).get('contributors_count', 0)
                    metrics['minor_contributors_count'] = contributors_count.get(filepath, {}).get('minor_contributors_count', 0)
                    metrics['highest_experience'] = highest_contributors_experience.get(filepath, 0)
                    metrics['commit_hunks_count'] = hunks_count.get(filepath, 0)
                    metrics['median_hunks_count'] = median_hunks_count.get(filepath, 0)
                    metrics['added_loc'] = lines_count.get(filepath, {}).get('added', 0)
                    metrics['removed_loc'] = lines_count.get(filepath, {}).get('removed', 0)
                    metrics['norm_added_loc'] = lines_count.get(filepath, {}).get('norm_added', 0)
                    metrics['norm_removed_loc'] = lines_count.get(filepath, {}).get('norm_removed', 0)
                    metrics['total_added_loc'] = lines_count.get(filepath, {}).get('total_added', 0)
                    metrics['total_removed_loc'] = lines_count.get(filepath, {}).get('total_removed', 0)

                    # Compute structural metrics
                    try:
                        structural = self.__code_metrics_extractor.run(StringIO(content.decoded_content))

                        for item in structural:    
                            if structural[item]['count'] is None:
                                break

                            for k in structural[item]:
                                metric = f'{item}_{k}'
                                metrics[metric] = structural[item][k]
                    except LoadingError:
                        print('\033[91m' + 'Error: failed to load {}. Insert a valid file!'.format('FILENAME HERE') + '\033[0m')
                    except yaml.YAMLError:
                        print('The input file is not a yaml file')
                    except Exception:
                        print('An unknown error has occurred')
                                
                    metrics_list.append(metrics)

                    dataset = pd.DataFrame(metrics_list)
                    with open(os.path.join('data', 'metrics.csv'), 'w') as out:
                        dataset.to_csv(out, mode='w', index=False)

            return dataset
