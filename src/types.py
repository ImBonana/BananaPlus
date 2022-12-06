from src.errors import InvalidSyntaxError, RTError, Context
from src.results import RTResult
from src.symbol_table import SymbolTable
from src.rt_types import *
import os
import math

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
        elif isinstance(other, List):
            return String(self.value + str(other.elements)).set_context(self.context), None
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

    def __str__(self):
        return self.value

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
        copy = Null()
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
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        list_ = []
        for x in self.elements:
            if isinstance(x, String):
                list_.append(x.__repr__())
            else:
                list_.append(str(x))
        return f'[{", ".join(list_)}]'

class BaseFunction(Type):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)}, too few args passed into '{self.name}'",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
         for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()

        res.register(self.check_args(arg_names, args))
        if res.error: return res
        self.populate_args(arg_names, args, exec_ctx)
        
        return res.success(None)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_null):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_null = should_return_null

    def execute(self, args):
        res = RTResult()
        from src.interpreter import Interpreter
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, exec_ctx))
        if res.error: return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.error: return res
        return res.success(Null() if self.should_return_null else value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error: return res

        return_value = res.register(method(exec_ctx))
        if res.error: return res

        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f"No execute_{self.name} method define")

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get("value")))
        return RTResult().success(Null())
    execute_print.arg_names = ["value"]
    
    def execute_input(self, exec_ctx):
        text = input(str(exec_ctx.symbol_table.get("value")))
        return RTResult().success(String(text))
    execute_input.arg_names = ["value"]
    
    def execute_input_int(self, exec_ctx):
        text = input(str(exec_ctx.symbol_table.get("value")))
        try:
            number = int(text)
        except ValueError:
            return RTResult().success(Null())
        return RTResult().success(Number(number))
    execute_input_int.arg_names = ["value"]

    def execute_clear(self, exec_ctx):
        os.system("cls" if os.name == "nt" else 'clear')
        return RTResult().success(Null())
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Boolean(is_number))
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Boolean(is_string))
    execute_is_string.arg_names = ["value"]

    def execute_is_boolean(self, exec_ctx):
        is_boolean = isinstance(exec_ctx.symbol_table.get("value"), Boolean)
        return RTResult().success(Boolean(is_boolean))
    execute_is_boolean.arg_names = ["value"]

    def execute_is_null(self, exec_ctx):
        is_null = isinstance(exec_ctx.symbol_table.get("value"), Null)
        return RTResult().success(Boolean(is_null))
    execute_is_null.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Boolean(is_list))
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Boolean(is_function))
    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(Null())
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Element at this index could not be removed from list because index is out of bounds",
                exec_ctx
            ))
        return RTResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))
        
        if not isinstance(listB, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Null())
    execute_extend.arg_names = ["listA", "listB"]

BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_boolean = BuiltInFunction("is_boolean")
BuiltInFunction.is_null = BuiltInFunction("is_null")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")

Number.math_PI = Number(math.pi)

def register_var(global_symbol_table):
    global_symbol_table.set("math_pi", Number.math_PI)

    global_symbol_table.set("print", BuiltInFunction.print)
    global_symbol_table.set("input", BuiltInFunction.input)
    global_symbol_table.set("input_int", BuiltInFunction.input_int)
    global_symbol_table.set("clear", BuiltInFunction.clear)
    global_symbol_table.set("is_number", BuiltInFunction.is_number)
    global_symbol_table.set("is_string", BuiltInFunction.is_string)
    global_symbol_table.set("is_boolean", BuiltInFunction.is_boolean)
    global_symbol_table.set("is_null", BuiltInFunction.is_null)
    global_symbol_table.set("is_list", BuiltInFunction.is_list)
    global_symbol_table.set("is_function", BuiltInFunction.is_function)
    global_symbol_table.set("append", BuiltInFunction.append)
    global_symbol_table.set("pop", BuiltInFunction.pop)
    global_symbol_table.set("extend", BuiltInFunction.extend)