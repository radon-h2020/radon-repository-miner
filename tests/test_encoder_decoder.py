import unittest
from repominer.files import FixedFile, FixedFileEncoder, FixedFileDecoder, FailureProneFile, FailureProneFileEncoder, FailureProneFileDecoder


class TestFixedFileEncoderAndDecoder(unittest.TestCase):

    def test_encoder(self):
        ff1 = FixedFile(filepath='file1.yml', fic='123', bic='456')
        encoded = FixedFileEncoder().default(ff1)
        assert type(encoded) == dict
        assert encoded == {
            "filepath": ff1.filepath,
            "fic": ff1.fic,
            "bic": ff1.bic
        }

    def test_decoder(self):
        ff1 = {
            "filepath": 'file1.yml',
            "fic": '123',
            "bic": 'failure-prone'
        }

        decoded = FixedFileDecoder().to_object(ff1)
        assert type(decoded) == FixedFile


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

        decoded = FailureProneFileDecoder().to_object(lf1)
        assert type(decoded) == FailureProneFile


if __name__ == '__main__':
    unittest.main()
