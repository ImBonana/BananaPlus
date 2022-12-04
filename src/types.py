from src.errors import InvalidSyntaxError, RTError, Context
from src.results import RTResult
from src.symbol_table import SymbolTable
from src.rt_types import *

class Type:
    def __init__(self):
        self.value = None
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)
    
    def dived_by(self, other):
        return None, self.illegal_operation(other)
    
    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return Boolean(self.value == other.value).set_context(self.context), None

    def get_comparison_ne(self, other):
        return Boolean(self.value != other.value).set_context(self.context), None

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return Boolean(other.is_true() and self.is_true()).set_context(self.context), None

    def ored_by(self, other):
        return Boolean(other.is_true() or self.is_true()).set_context(self.context), None

    def notted(self):
        return Boolean(not self.is_true()).set_context(self.context), None

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def is_true(self):
        return True

    def copy(self):
        copy = self(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(other.pos_start, other.pos_end, f"Can't do this operation with the type {type(other).__name__}", self.context)

    def __repr__(self):
        return str(self.value)

class Number(Type):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        elif isinstance(other, Null):
            return Number(self.value + 0).set_context(self.context), None
        elif isinstance(other, String):
            return String(str(self.value) + other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        elif isinstance(other, Null):
            return Number(self.value - 0).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        elif isinstance(other, Null):
            return Number(self.value * 0).set_context(self.context), None
        return None, Type.illegal_operation(self, other)
    
    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, "Division by zero", self.context)
            return Number(self.value / other.value).set_context(self.context), None
        elif isinstance(other, Null):
            return None, RTError(other.pos_start, other.pos_end, "Division by null", self.context)
        return None, Type.illegal_operation(self, other)
    
    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        elif isinstance(other, Null):
            return Number(self.value ** 0).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Boolean(self.value < other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Boolean(self.value > other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Boolean(self.value <= other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Boolean(self.value >= other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy


    def __repr__(self):
        return str(self.value)

class String(Type):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Boolean):
            return String(self.value + KEYWORDS[str(other.value).upper()]).set_context(self.context), None
        elif isinstance(other, Null):
            return String(self.value + KEYWORDS.NULL).set_context(self.context), None
        return String(self.value + str(other.value)).set_context(self.context), None

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'"{self.value}"'

class Boolean(Type):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(KEYWORDS[str(self.value).upper()] + other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def is_true(self):
        return self.value

    def copy(self):
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)

class Null(Type):
    def __init__(self):
        super().__init__()
        self.value = None

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(0 + other.value).set_context(self.context), None
        elif isinstance(other, String):
            return String(KEYWORDS.NULL + other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(0 - other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(0 * other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)
    
    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, "Division by zero", self.context)
            return Number(0 / other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)
    
    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(0 ** other.value).set_context(self.context), None
        return None, Type.illegal_operation(self, other)

    def is_true(self):
        return False

    def copy(self):
        copy = Null(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return KEYWORDS.NULL

class List(Type):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                    other.pos_end, other.pos_end,
                    "Element at this index could not be removed from list because index is out of bounds.",
                    self.context
                )
        return None, Type.illegal_operation(self, other)
    
    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        return None, Type.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                    other.pos_end, other.pos_end,
                    "Element at this index could not be retrived from list because index is out of bounds.",
                    self.context
                )
        return None, Type.illegal_operation(self, other)

    def copy(self):
        copy = List(self.elements[:])
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'

class Function(Type):
    def __init__(self, name, body_node, arg_names):
        super().__init__()
        self.name = name or "<anonymous>"
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        from src.interpreter import Interpreter
        interpreter = Interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args) > len(self.arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(self.arg_names)} too many args passed into '{self.name}'",
                self.context
            ))
        
        if len(args) < len(self.arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args)}, too few args passed into '{self.name}'",
                self.context
            ))

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error: return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<function {self.name}>"