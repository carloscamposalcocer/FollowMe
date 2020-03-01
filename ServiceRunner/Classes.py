class Item:
    def __init__(self, frame=0, time=0.0, label=-1, score=0, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.label = int(label)
        self.score = score
        self.frame = frame
        self.time = time

    def __str__(self):
        return f"Frame {self.frame} Item from X[{self.xmin:0.2f}->{self.xmax:0.2f}] Y[{self.ymin:0.2f}->{self.ymax:0.2f}]"


class Relation:
    def __init__(self, score, pair):
        self.score = score
        self.pair = pair

    def __str__(self):
        return f"{self.pair[0]} -> {self.pair[1]} with score {self.score}"

    def __repr__(self):
        return self.__str__()
