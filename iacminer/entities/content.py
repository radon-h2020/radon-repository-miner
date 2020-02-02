class ContentFile():

    def __init__(self, filepath: str, content: str, defective: bool = False):
        """
        Initialize a new content file.
        """
        self.filepath = filepath
        self.content = content
        self.defective = defective
