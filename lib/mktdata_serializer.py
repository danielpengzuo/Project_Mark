class DictCsvSerializer:
    def __init__(self, fields):
        self._fields = fields


    def header(self):
        return ','.join(self._fields)


    def dict_to_row(self, dct):
        return ','.join(str(dct[f]) for f in self._fields)
