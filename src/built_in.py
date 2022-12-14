from src.types import BaseFunction, Number, String, Null, Boolean, List, Object
import math
from src.results import RTResult
import os
from src.errors import RTError

class BuiltInFunction(BaseFunction):
    def __init__(self, name, this=None):
        super().__init__(name)
        self.this = this

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res

        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f"No execute_{self.name} method define")

    def copy(self):
        copy = BuiltInFunction(self.name, self.this)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get("value")))
        return RTResult().success(Null())
    execute_print.arg_names = [("value", False)]
    
    def execute_input(self, exec_ctx):
        text = input(str(exec_ctx.symbol_table.get("value")))
        if text == None: text = ""
        return RTResult().success(String(text))
    execute_input.arg_names = [("value", True)]
    
    def execute_input_int(self, exec_ctx):
        text = input(str(exec_ctx.symbol_table.get("value")))
        if isinstance(text, Null) : text = "0"
        try:
            number = int(text)
        except ValueError:
            return RTResult().success(Null())
        return RTResult().success(Number(number))
    execute_input_int.arg_names = [("value", True)]

    def execute_clear(self, exec_ctx):
        os.system("cls" if os.name == "nt" else 'clear')
        return RTResult().success(Null())
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Boolean(is_number))
    execute_is_number.arg_names = [("value", False)]

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Boolean(is_string))
    execute_is_string.arg_names = [("value", False)]

    def execute_is_boolean(self, exec_ctx):
        is_boolean = isinstance(exec_ctx.symbol_table.get("value"), Boolean)
        return RTResult().success(Boolean(is_boolean))
    execute_is_boolean.arg_names = [("value", False)]

    def execute_is_null(self, exec_ctx):
        is_null = isinstance(exec_ctx.symbol_table.get("value"), Null)
        return RTResult().success(Boolean(is_null))
    execute_is_null.arg_names = [("value", False)]

    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Boolean(is_list))
    execute_is_list.arg_names = [("value", False)]

    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Boolean(is_function))
    execute_is_function.arg_names = [("value", False)]

    def execute_append(self, exec_ctx):
        list_ = self.this
        value = exec_ctx.symbol_table.get("value")

        list_.elements.append(value)
        return RTResult().success(Null())
    execute_append.arg_names = [("value", False)]

    def execute_pop(self, exec_ctx):
        list_ = self.this
        index = exec_ctx.symbol_table.get("index")
        if isinstance(index, Null): index = Number(len(list_.elements)-1)

        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be number",
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
    execute_pop.arg_names = [("index", True)]

    def execute_extend(self, exec_ctx):
        listA = self.this
        listB = exec_ctx.symbol_table.get("list")

        if not isinstance(listB, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Null())
    execute_extend.arg_names = [("list", False)]

    def execute_len(self, exec_ctx):
        value = exec_ctx.symbol_table.get("value")
        
        leng = -1

        if isinstance(value, List):
            leng = len(value.elements)
        elif isinstance(value, String):
            leng = len(value.value)
        else:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list or string",
                exec_ctx
            ))

        return RTResult().success(Number(leng))
    execute_len.arg_names = [("value", False)]

    def execute_String(self, exec_ctx):
        value = exec_ctx.symbol_table.get("value")
        return RTResult().success(String(str(value)))
    execute_String.arg_names = [("value", False)]
    
    def execute_Number(self, exec_ctx):
        value = exec_ctx.symbol_table.get("value")
        if isinstance(value, String):
            try:
                value = Number(int(value.value))
            except:
                return RTResult().failure(RTError(
                    self.pos_start, self.pos_end,
                    "A string argument must contain at least one number",
                    exec_ctx
                ))
        elif isinstance(value, Boolean):
            if value.value == True:
                value = Number(1)
            else:
                value = Number(0)
        else:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "The argument must be a string or boolean",
                exec_ctx
            ))

        return RTResult().success(value)
    execute_Number.arg_names = [("value", False)]
    
    def execute_Boolean(self, exec_ctx):
        value = exec_ctx.symbol_table.get("value")
        if isinstance(value, String):
            value = Boolean("true" in value.value.lower())
        elif isinstance(value, Number):
           value = Boolean(1 == value.value)
        else:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "The argument must be a string or number",
                exec_ctx
            ))

        return RTResult().success(value)
    execute_Boolean.arg_names = [("value", False)]


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
BuiltInFunction.string = BuiltInFunction("String")
BuiltInFunction.number = BuiltInFunction("Number")
BuiltInFunction.boolean = BuiltInFunction("Boolean")
BuiltInFunction.len = BuiltInFunction("len")

global_math = Object({
    "pi": Number(math.pi),
    "inf": Number(math.inf)
})

global_vars = {
    "math": global_math,
    "print": BuiltInFunction.print,
    "input": BuiltInFunction.input,
    "input_int": BuiltInFunction.input_int,
    "clear": BuiltInFunction.clear,
    "is_number": BuiltInFunction.is_number,
    "is_string": BuiltInFunction.is_string,
    "is_boolean": BuiltInFunction.is_boolean,
    "is_null": BuiltInFunction.is_null,
    "is_list": BuiltInFunction.is_list,
    "is_function": BuiltInFunction.is_function,
    "String": BuiltInFunction.string,
    "Number": BuiltInFunction.number,
    "Boolean": BuiltInFunction.boolean,
    "len": BuiltInFunction.len
}

def register_var(symbol_table):
    for name, value in global_vars.items():
        symbol_table.set(name, value)

def unregister_var(symbol_table):
    for name in global_vars.keys():
        symbol_table.remove(name)