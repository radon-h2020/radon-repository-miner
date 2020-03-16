from iacminer.entities.file import LabeledFile

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
        f1 = LabeledFile('filenameA', 'a123bc', None, None, None)
        f2 = LabeledFile('filenameA', 'a123bc', None, None, None)
        f3 = LabeledFile('filenameA', 'b234cd', None, None, None)
        f4 = LabeledFile('filenameB', 'b234cd', None, None, None)
        f5 = LabeledFile('filenameB', 'b234ce', None, None, None)

        assert f1 == f2
        assert f1 != f3
        assert f1 != f4
        assert f1 != f5
        assert f3 != f4
        assert f3 != f5

    def test_in(self):
        f1 = LabeledFile('filenameA', 'a123bc', None, None, None)
        f2 = LabeledFile('filenameA', 'a123bc', None, None, None)
        f3 = LabeledFile('filenameA', 'b234cd', None, None, None)
        f4 = LabeledFile('filenameB', 'b234cd', None, None, None)
        f5 = LabeledFile('filenameB', 'b234ce', None, None, None)

        list1 = [f2, f3, f4, f5]
        list2 = [f3, f4, f5]

        assert f1 in list1
        assert f1 not in list2

