from iacminer.entities.file import FixingFile

class TestClass():

    def test_eq(self):
        f1 = FixingFile('filenameA', 'fix1', {'bic1', 'bic2'})
        f2 = FixingFile('filenameA', 'fix2', {'bic3', 'bic4'})
        f3 = FixingFile('filenameA', 'fix2', {'bic1'})
        f4 = FixingFile('filenameB', 'fix1', {'bic1'})

        assert f1 == f2
        assert f1 == f3
        assert f1 != f4


