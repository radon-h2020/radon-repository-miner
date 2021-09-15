import unittest
from repominer.files import FixedFile, FixedFileEncoder, FixedFileDecoder, FailureProneFile, FailureProneFileEncoder, \
    FailureProneFileDecoder


class TestFilesTestSuite(unittest.TestCase):

    # Tests for FixedFile class

    def test_fixed_file_eq_true(self):
        ff1 = FixedFile(filepath='file1.yml', fic='123', bic='456')
        ff2 = FixedFile(filepath='file1.yml', fic='123', bic='456')

        assert ff1 == ff2
        assert ff1 in [ff2]

    def test_fixed_file_eq_false(self):
        ff1 = FixedFile(filepath='file1.yml', fic='123', bic='456')
        ff2 = FixedFile(filepath='file2.yml', fic='123', bic='456')

        assert ff1 != ff2
        assert ff1 not in [ff2]

    def test_fixed_file_eq_false_instance(self):
        ff1 = FixedFile(filepath='file1.yml', fic='123', bic='456')
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')

        assert ff1 != lf1

    def test_fixed_file_encoder(self):
        ff1 = FixedFile(filepath='file1.yml', fic='123', bic='456')
        encoded = FixedFileEncoder().default(ff1)
        assert type(encoded) == dict
        assert encoded == {
            "filepath": ff1.filepath,
            "fic": ff1.fic,
            "bic": ff1.bic
        }

    def test_fixed_file_encoder_none(self):
        """Pass a FailureProneFile instance instead of a FixedFile instance to FixedFileEncoder to test the instance is
        correct
        """
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')
        encoded = FixedFileEncoder().default(lf1)
        assert encoded is None

    def test_fixed_file_decoder(self):
        ff1 = {
            "filepath": 'file1.yml',
            "fic": '123',
            "bic": 'failure-prone'
        }

        decoded = FixedFileDecoder().to_object(ff1)
        assert type(decoded) == FixedFile

    def test_fixed_file_decoder_none(self):
        """Pass a list to the FixedFileDecoder to test the input type is correct"""
        ff1 = {
            "filepath": 'file1.yml',
            "fic": '123',
            "bic": 'failure-prone'
        }

        decoded = FixedFileDecoder().to_object([ff1])
        assert decoded is None

    # Tests for FailureProneFile class

    def test_failure_prone_file_eq_true(self):
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')
        lf2 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')
        lf3 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')

        assert lf1 == lf2 == lf3
        assert lf1 in [lf2, lf3]

    def test_failure_prone_file_eq_false(self):
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')
        lf2 = FailureProneFile(filepath='file1.yml', commit='456', fixing_commit='456')
        lf3 = FailureProneFile(filepath='file2.yml', commit='123', fixing_commit='456')

        assert lf1 != lf2 != lf3
        assert lf1 not in [lf2, lf3]

    def test_failure_prone_file_eq_false_instance(self):
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')
        ff1 = FixedFile(filepath='file2.yml', fic='123', bic='456')

        assert lf1 != ff1

    def test_failure_prone_file_encoder(self):
        lf1 = FailureProneFile(filepath='file1.yml', commit='123', fixing_commit='456')

        encoded = FailureProneFileEncoder().default(lf1)
        assert type(encoded) == dict
        assert encoded == {
            "filepath": lf1.filepath,
            "commit": lf1.commit,
            "fixing_commit": lf1.fixing_commit
        }

    def test_failure_prone_file_encoder_none(self):
        """Pass a FixedFile instance instead of a FailureProneFile instance to FailureProneFileEncoder to test the
        instance is correct
        """
        ff1 = FixedFile(filepath='file2.yml', fic='123', bic='456')
        encoded = FailureProneFileEncoder().default(ff1)
        assert encoded is None

    def test_failure_prone_file_decoder(self):
        lf1 = {
            "filepath": 'file1.yml',
            "commit": '123',
            "fixing_commit": 'failure-prone'
        }

        decoded = FailureProneFileDecoder().to_object(lf1)
        assert type(decoded) == FailureProneFile

    def test_failure_prone_file_decoder_none(self):
        """Pass a list to the FailureProneFileDecoder to test the input type is correct"""
        lf1 = {
            "filepath": 'file1.yml',
            "commit": '123',
            "fixing_commit": 'failure-prone'
        }

        decoded = FailureProneFileDecoder().to_object([lf1])
        assert decoded is None


if __name__ == '__main__':
    unittest.main()
