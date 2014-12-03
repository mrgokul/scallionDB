class Select(object):
    def __init__(self, conditions):
        self.conditions = conditions
        self.stack = []
    def next(self)