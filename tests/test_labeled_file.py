import unittest
from radonminer.file import LabeledFile, LabeledFileEncoder, LabeledFileDecoder

import json
class TestLabeledFile(unittest.TestCase):

    def test_encoder(self):
        lf1 = LabeledFile(filepath='file1.yml', commit='123', fixing_commit='456', label=LabeledFile.Label.FAILURE_PRONE)

        encoded = LabeledFileEncoder().default(lf1)
        assert type(encoded) == dict
        assert encoded == {
            "filepath": lf1.filepath,
            "commit": lf1.commit,
            "label": 'failure-prone',
            "fixing_commit": lf1.fixing_commit
        }

    def test_decoder(self):
        lf1 = {
            "filepath": 'file1.yml',
            "commit": '123',
            "label": '456',
            "fixing_commit": 'failure-prone'
        }

        decoded = LabeledFileDecoder().object_hook(lf1)
        assert type(decoded) == LabeledFile


if __name__ == '__main__':
    unittest.main()
