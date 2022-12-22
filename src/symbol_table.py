class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name, default=None):
        value = self.symbols.get(name, default)
        if value == None and self.parent:
            return self.parent.get(name, default)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

    def copy(self):
        new_symbol_table = SymbolTable(self.parent)
        new_symbol_table.symbols = self.symbols
        return new_symbol_table