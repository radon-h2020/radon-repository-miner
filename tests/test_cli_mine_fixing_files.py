# !/usr/bin/python
# coding=utf-8

import json
import os
import shutil
import unittest

from repominer.files import FixedFile, FixedFileEncoder


class CLIMineFixedFilesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path_to_tmp_dir = os.path.join(os.getcwd(), 'test_data', 'tmp')
        os.mkdir(cls.path_to_tmp_dir)
        os.environ["TMP_REPOSITORIES_DIR"] = cls.path_to_tmp_dir

        # File containing commits to exclude
        cls.exclude_fixed_files_file = os.path.join(cls.path_to_tmp_dir, 'exclude_files.json')

        fixed_files = [
            FixedFile(filepath=os.path.join('policies', 'placement', 'requirement', 'location',
                                             'tosca_policy_Placement_Requirement_location.yaml'),
                      fic='3994a835f7417703810c95555bf3553b9dcaea9b',
                      bic='undefined'),
            FixedFile(filepath=os.path.join('policies', 'scalability', 'consumption',
                                             'tosca_policy_scalability_comsumption.yaml'),
                      fic='3994a835f7417703810c95555bf3553b9dcaea9b',
                      bic='undefined'),
            FixedFile(filepath=os.path.join('policies', 'scalability', 'performance', 'completion',
                                             'tosca_policy_scalability_performance_completion.yaml'),
                      fic='3994a835f7417703810c95555bf3553b9dcaea9b',
                      bic='undefined'),
            FixedFile(filepath=os.path.join('templates', 'dataavenue.yaml'),
                      fic='3994a835f7417703810c95555bf3553b9dcaea9b',
                      bic='undefined'),
            FixedFile(filepath=os.path.join('templates', 'inycom.yaml'),
                      fic='3994a835f7417703810c95555bf3553b9dcaea9b',
                      bic='undefined'),
            FixedFile(filepath=os.path.join('templates', 'repast.yaml'),
                      fic='3994a835f7417703810c95555bf3553b9dcaea9b',
                      bic='undefined')
        ]

        json_files = []
        for file in fixed_files:
            json_files.append(FixedFileEncoder().default(file))

        with open(cls.exclude_fixed_files_file, 'w') as f:
            json.dump(json_files, f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.path_to_tmp_dir)
        del os.environ["TMP_REPOSITORIES_DIR"]

    def test_mine_fixed_files(self):
        result = os.system(
            'repo-miner mine fixed-files github tosca UoW-CPC/COLARepo {}'.format(self.path_to_tmp_dir))

        assert result == 0

        with open(os.path.join(self.path_to_tmp_dir, 'fixed-files.json'), 'r') as f:
            fixed_files = json.load(f)
            assert len(fixed_files) == 7

    def test_mine_fixed_files_with_exclude(self):
        result = os.system(
            'repo-miner mine fixed-files github tosca UoW-CPC/COLARepo {0} --exclude-files {1}'.format(
                self.path_to_tmp_dir,
                self.exclude_fixed_files_file))

        assert result == 0

        with open(os.path.join(self.path_to_tmp_dir, 'fixed-files.json'), 'r') as f:
            fixed_files = json.load(f)
            assert len(fixed_files) == 1


if __name__ == '__main__':
    unittest.main()
