import itertools


class PersonId:
    id_iterator = itertools.count()

    # Start with ID 1
    id_iterator.__next__()

    def __init__(self):
        self.id = next(self.id_iterator)
