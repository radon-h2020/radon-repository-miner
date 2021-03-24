# !/usr/bin/python
# coding=utf-8

import json
import os
import shutil
import unittest

from argparse import Namespace
from repominer.cli import MinerCLI

class CLIMinerInitTestCase(unittest.TestCase):

    def test_init_no_host(self):
        args = Namespace()

        try:
            MinerCLI(args)
        except SystemExit as exc:
            assert exc.code == 1

    def test_init_wrong_host(self):
        args = Namespace(host='wrong')

        try:
            MinerCLI(args)
        except SystemExit as exc:
            assert exc.code == 1

    def test_init_no_language(self):
        args = Namespace(host='github', repository='radon-h2020/radon-repository-miner')

        try:
            MinerCLI(args)
        except SystemExit as exc:
            assert exc.code == 2
            
    def test_init_wrong_language(self):
        args = Namespace(host='github', repository='radon-h2020/radon-repository-miner', language='wrong')

        try:
            MinerCLI(args)
        except SystemExit as exc:
            assert exc.code == 2

if __name__ == '__main__':
    unittest.main()
