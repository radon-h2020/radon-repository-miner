from iacminer.entities.file import FixingFile

class TestClass():

    def setup_class(self):
       pass

    def teardown_class(self):
        pass

    def setup_method(self):
        pass

    def teardown_method(self):
        pass


    def test_eq(self):
        f1 = FixingFile('filenameA', 'fix1', 'bic1')
        f2 = FixingFile('filenameA', 'fix1', 'bic2')
        f3 = FixingFile('filenameA', 'fix2', 'bic1')
        f4 = FixingFile('filenameB', 'fix1', 'bic1')

        assert f1 == f2
        assert f1 == f3
        assert f1 != f4


