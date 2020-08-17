class Line:
    def __init__(self, line_number, text):
        self.line_number = line_number
        self.text = text

    def __repr__(self):
        return self.text
