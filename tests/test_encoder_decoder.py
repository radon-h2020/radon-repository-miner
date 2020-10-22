import unittest
from radonminer.files import FailureProneFile, FailureProneFileEncoder, FailureProneFileDecoder


class TestFailureProneFileEncoderAndDecoder(unittest.TestCase):

    def test_encoder(self):
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')

        encoded = FailureProneFileEncoder().default(lf1)
        assert type(encoded) == dict
        assert encoded == {
            "filepath": lf1.filepath,
            "commit": lf1.commit,
            "fixing_commit": lf1.fixing_commit
        }

    def test_decoder(self):
        lf1 = {
            "filepath": 'file1.yml',
            "commit": '123',
            "fixing_commit": 'failure-prone'
        }

        decoded = FailureProneFileDecoder().object_hook(lf1)
        assert type(decoded) == FailureProneFile


if __name__ == '__main__':
    unittest.main()
