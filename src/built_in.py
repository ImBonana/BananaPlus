from src.types import BaseFunction, Number, String, Null, Boolean, List, Object
import math
from src.results import RTResult
import os
from src.errors import RTError
from src.rt_types import LETTERS_DIGITS, DIGITS

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

    def execute_toLowerCase(self, exec_ctx):
        string = self.this
        string.value = string.value.lower()
        return RTResult().success(string)
    execute_toLowerCase.arg_names = []        
    
    def execute_toUpperCase(self, exec_ctx):
        string = self.this
        string.value = string.value.upper()
        return RTResult().success(string)
    execute_toUpperCase.arg_names = []        
    
    def execute_replace(self, exec_ctx):
        string = self.this
        find = exec_ctx.symbol_table.get("find")
        replace = exec_ctx.symbol_table.get("replace")

        if not isinstance(find, String) or not isinstance(replace, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "All arguments must be a string",
                exec_ctx
            ))

        string.value = string.value.replace(find.value, replace.value)
        return RTResult().success(string)
    execute_replace.arg_names = [("find", False), ("replace", False)]

    def execute_startsWith(self, exec_ctx):
        string = self.this
        char = exec_ctx.symbol_table.get("characters")
        if not isinstance(char, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a string",
                exec_ctx
            ))
        return RTResult().success(Boolean(string.value.startswith(char.value)))
    execute_startsWith.arg_names = [("characters", False)]
    
    def execute_endsWith(self, exec_ctx):
        string = self.this
        char = exec_ctx.symbol_table.get("characters")
        if not isinstance(char, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a string",
                exec_ctx
            ))
        return RTResult().success(Boolean(string.value.endswith(char.value)))
    execute_endsWith.arg_names = [("characters", False)]

    def execute_indexOf(self, exec_ctx):
        string = self.this
        find = exec_ctx.symbol_table.get("find")
        if not isinstance(find, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a string",
                exec_ctx
            ))
        return RTResult().success(Number(string.value.find(find.value)))
    execute_indexOf.arg_names = [("find", False)]

    def execute_isAllNum(self, exec_ctx):
        string = self.this
        return RTResult().success(Boolean(string.value.isnumeric()))
    execute_isAllNum.arg_names = []

    def execute_isAllAlpha(self, exec_ctx):
        string = self.this
        return RTResult().success(Boolean(string.value.isalpha()))
    execute_isAllAlpha.arg_names = []

    def execute_isSpace(self, exec_ctx):
        string = self.this
        return RTResult().success(Boolean(string.value.isspace()))
    execute_isSpace.arg_names = []

    def execute_split(self, exec_ctx):
        string = self.this
        char = exec_ctx.symbol_table.get("character")
        if not isinstance(char, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a string",
                exec_ctx
            ))

        elements = []
        for part in string.value.split(char.value):
            elements.append(String(part))

        return RTResult().success(List(elements))
    execute_split.arg_names = [("character", False)]

    def execute_trim(self, exec_ctx):
        string = self.this
        string.value = string.value.strip()
        return RTResult().success(string)
    execute_trim.arg_names = []

    def execute_sub(self, exec_ctx):
        string = self.this
        pos = exec_ctx.symbol_table.get("position")
        count = exec_ctx.symbol_table.get("count")
        
        if not isinstance(pos, Number) or not isinstance(count, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First and second argument must be a number",
                exec_ctx
            ))

        if pos.value < 0 or pos.value >= len(string.value):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument (Position) can't be below 0 and more than the string length",
                exec_ctx
            ))

        if count.value < 1:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Decond argument (Count) can't be below 1",
                exec_ctx
            ))

        string.value = string.value[:pos.value] + string.value[pos.value+count.value:]
        return RTResult().success(string)
    execute_sub.arg_names = [("position", False), ("count", False)]

    def execute_includes(self, exec_ctx):
        string = self.this
        _str = exec_ctx.symbol_table.get("str")

        if not isinstance(_str, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a string",
                exec_ctx
            ))

        return RTResult().success(Boolean(_str.value in string.value))
    execute_includes.arg_names = [("str", False)]

    def execute_to_letters(self, exec_ctx):
        string = self.this
        
        letter_list = []

        for i in string.value:
            letter_list.append(String(i))

        return RTResult().success(List(letter_list))
    execute_to_letters.arg_names = []

    def execute_readFile(self, exec_ctx):
        file_name = exec_ctx.symbol_table.get("file_name")
        
        if not isinstance(file_name, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "The argument must be a string",
                exec_ctx
            ))

        from BananaPlus import workspace_dir

        file_to_open = file_name

        if file_name.value.startswith("./"):
            file_to_open = workspace_dir + "\\" + file_name.value[2:].replace("/", "\\")
        
        try:
            file =  open(file_to_open, 'r')
            file_data = file.read()
            file.close()
            return RTResult().success(String(file_data))
        except Exception as e:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Can't open that file",
                exec_ctx
            ))
    execute_readFile.arg_names = [("file_name", False)]  
    
    def execute_writeFile(self, exec_ctx):
        file_name = exec_ctx.symbol_table.get("file_name")
        data = exec_ctx.symbol_table.get("data")

        if not isinstance(file_name, String) or not isinstance(data, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "All arguments must be a string",
                exec_ctx
            ))

        from BananaPlus import workspace_dir

        file_to_open = file_name

        if file_name.value.startswith("./"):
            file_to_open = workspace_dir + "\\" + file_name.value[2:].replace("/", "\\")
        
        try:
            file = open(file_to_open, 'w')
            file.write(data.value)
            file.close()
            return RTResult().success(data.copy())
        except Exception as e:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Can't write in that file",
                exec_ctx
            ))
    execute_writeFile.arg_names = [("file_name", False), ("data", False)]

    def execute_deleteFile(self, exec_ctx):
        file_name = exec_ctx.symbol_table.get("file_name")
        
        if not isinstance(file_name, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "The argument must be a string",
                exec_ctx
            ))

        from BananaPlus import workspace_dir

        file_to_delete = file_name

        if file_name.value.startswith("./"):
            file_to_delete = workspace_dir + "\\" + file_name.value[2:].replace("/", "\\")
        
        if os.path.exists(file_to_delete):
            try:
                os.remove(file_to_delete)              
            except Exception as e:
                return RTResult().failure(RTError(
                    self.pos_start, self.pos_end,
                    "Can't delete that file",
                    exec_ctx
                ))
        else:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "File does not exist",
                exec_ctx
            ))
        
        return RTResult().success(Null())
    execute_deleteFile.arg_names = [("file_name", False)]  

    def execute_object_set(self, exec_ctx):
        obj = self.this
        key = exec_ctx.symbol_table.get("key")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(key, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument (key) must be a string",
                exec_ctx
            ))

        first_letter = True
        err = False
        for i in key.value:
            if first_letter and i in DIGITS:
                err = True
                break
            if i not in LETTERS_DIGITS + "_":
                err = True
                break
            first_letter = False

        if err: 
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument (key) is invalid",
                exec_ctx
            ))

        obj.elements[key.value] = value

        return RTResult().success(obj)
    execute_object_set.arg_names = [("key", False), ("value", False)]

    def execute_object_get(self, exec_ctx):
        obj = self.this
        key = exec_ctx.symbol_table.get("key")
        default = exec_ctx.symbol_table.get("default", None)

        if not isinstance(key, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument (key) must be a string",
                exec_ctx
            ))

        return RTResult().success(obj.elements.get(key.value, Null() if not default else default))
    execute_object_get.arg_names = [("key", False), ("default", True)]

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
BuiltInFunction.read_file = BuiltInFunction("readFile")
BuiltInFunction.write_file = BuiltInFunction("writeFile")
BuiltInFunction.delete_file = BuiltInFunction("deleteFile")

global_math = Object({
    "pi": Number(math.pi),
    "inf": Number(math.inf)
})

global_File = Object({
    "readFile": BuiltInFunction.read_file,
    "writeFile": BuiltInFunction.write_file,
    "deleteFile": BuiltInFunction.delete_file
})

global_vars = {
    "Math": global_math,
    "Files": global_File,
    "print": BuiltInFunction.print,
    "input": BuiltInFunction.input,
    "inputInt": BuiltInFunction.input_int,
    "clear": BuiltInFunction.clear,
    "isNumber": BuiltInFunction.is_number,
    "isString": BuiltInFunction.is_string,
    "isBoolean": BuiltInFunction.is_boolean,
    "isNull": BuiltInFunction.is_null,
    "isList": BuiltInFunction.is_list,
    "isFunction": BuiltInFunction.is_function,
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