class Movement(object):
    vector = (0,0)
    start = 0.0
    duration = 0.0

    def __init__(self, vector, start, duration):
        self.vector = vector
        self.start = start
        self.duration = duration