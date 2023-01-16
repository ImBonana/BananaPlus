from src.errors import InvalidSyntaxError, RTError, Context
from src.results import RTResult
from src.symbol_table import SymbolTable
from src.rt_types import *
from src.token import Token

class Type:
    def __init__(self):
        self.value = None
        self.elements = None
        self.built_in = {  }
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def dotted_to(self, other, pos_start=None, pos_end=None):
        if not pos_start: pos_start = self.pos_start
        if not pos_end: pos_end = self.pos_end
        if other in self.built_in:
            return self.built_in.get(other, Null().set_context(self.context)), None
        elif self.elements != None:
            if isinstance(self.elements, object):
                if other in self.elements:
                    return self.elements.get(other, Null().set_context(self.context)), None
        return None, RTError(
                        pos_start, pos_end,
                        f"'{other}' is not defined",
                        self.context
                    )

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
        return Boolean(self.equals(other)).set_context(self.context), None

    def get_comparison_ne(self, other):
        return Boolean(not self.equals(other)).set_context(self.context), None

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

    def equals(self, other):
        return self.__class__ == other.__class__

    def copy(self):
        copy = self(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def illegal_operation(self, other=None, show_type=True):
        if not other: other = self
        return RTError(other.pos_start, other.pos_end, f"Can't do this operation{' with the type' + type(other).__name__ if show_type else ''}.", self.context)

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

    def equals(self, other):
        return self.__class__ == other.__class__ and self.value == other.value

    def __repr__(self):
        return str(self.value)

class String(Type):
    def __init__(self, value):
        super().__init__()
        self.value = value

        from src.built_in import BuiltInFunction
        self.built_in = { 
            "toLowerCase": BuiltInFunction("toLowerCase", self),
            "toUpperCase": BuiltInFunction("toUpperCase", self),
            "replace": BuiltInFunction("replace", self),
            "startsWith": BuiltInFunction("startsWith", self),
            "endsWith": BuiltInFunction("endsWith", self),
            "indexOf": BuiltInFunction("indexOf", self),
            "isAllNum": BuiltInFunction("isAllNum", self),
            "isAllAlpha": BuiltInFunction("isAllAlpha", self),
            "isSpace": BuiltInFunction("isSpace", self),
            "split": BuiltInFunction("split", self),
            "trim": BuiltInFunction("trim", self),
            "sub": BuiltInFunction("sub", self),
            "includes": BuiltInFunction("includes", self),
            "toLetters": BuiltInFunction("to_letters", self)
        }

    def added_to(self, other):
        if isinstance(other, Boolean):
            return String(self.value + KEYWORDS[str(other.value).upper()]).set_context(self.context), None
        elif isinstance(other, Null):
            return String(self.value + KEYWORDS.NULL).set_context(self.context), None
        elif isinstance(other, List):
            return String(self.value + str(other.elements)).set_context(self.context), None
        return String(self.value + str(other)).set_context(self.context), None

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

    def equals(self, other):
        return self.__class__ == other.__class__ and self.value == other.value

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

    def equals(self, other):
        return self.__class__ == other.__class__ and self.value == other.value

    def __repr__(self):
        return f"{KEYWORDS.__dict__[str(self.value).upper()]}"

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
    
    def __str__(self):
        return KEYWORDS.NULL

class List(Type):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        
        from src.built_in import BuiltInFunction
        self.built_in = { 
            "extend": BuiltInFunction("extend", self),
            "pop": BuiltInFunction("pop", self),
            "append": BuiltInFunction("append", self)
        }
    
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

    def equals(self, other):
        return self.__class__ == other.__class__ and self.elements == other.elements

    def __repr__(self):
        list_ = []
        for x in self.elements:
            if isinstance(x, String):
                list_.append(x.__repr__())
            else:
                list_.append(str(x))
        return f'[{", ".join(list_)}]'

class Object(Type):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

        from src.built_in import BuiltInFunction
        self.built_in = {
            "set": BuiltInFunction("object_set", self),
            "get": BuiltInFunction("object_get", self)
        }

    def added_to(self, other):
        if isinstance(other, Object):
            new_object = self.copy()
            if len(other.elements.keys()) <= 0: return new_object, None

            for k, v in other.elements.items():
                new_object.elements[k] = v

            return new_object, None

        return None, Type.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, String):
            new_object = self.copy()
            del new_object.elements[other.value]
            return new_object, None
        return None, Type.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, String):
            try:
                return self.elements.get(other.value), None
            except:
                return None, RTError(
                    other.pos_end, other.pos_end,
                    "This element is not in the object",
                    self.context
                )
        return None, Type.illegal_operation(self, other)
        
    def copy(self):
        copy = Object(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def equals(self, other):
        return self.__class__ == other.__class__ and self.elements == other.elements

    def __repr__(self):
        string = "{  }"
        if len(self.elements.keys()) > 0:
            string = "{ "
            for k, v in self.elements.items():
                string += k + ": "
                if isinstance(v, String):
                    string += repr(v)
                elif isinstance(v, Object):
                    string += repr(v)
                else:
                    string += str(v)
                string += ", "
            string = string[:-2]
            string += " }"
        return string

class BaseFunction(Type):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self, context=None):
        new_context = Context(self.name, context if context != None else self.context, self.pos_start)
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
        
        firstOp = -1

        for i in range(len(arg_names)):
            if arg_names[i][1] == True:
                firstOp = i
                break


        if (len(args) <= firstOp-1) or ((firstOp < 0) and (len(args) < len(arg_names))):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)}, too few args passed into '{self.name}'",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(arg_names)):
            arg_name = arg_names[i][0]
            if isinstance(arg_name, Token):
                arg_name = arg_names[i][0].value

            if len(args)-1 < i:
                arg_value = Null()
            else:
                arg_value = args[i]

            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()

        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        
        return res.success(None)

    def equals(self, other):
        return self.__class__ == other.__class__ and self.name == other.name

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return, isPublic, lib):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return
        self.isPublic = isPublic
        self.lib = lib

    def execute(self, args):
        res = RTResult()
        from src.interpreter import Interpreter
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context(self.lib)

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None: return res
        
        ret_value = (value if self.should_auto_return else None) or res.func_return_value or Null()
        return res.success(ret_value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return, self.isPublic, self.lib)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<function {self.name}>"