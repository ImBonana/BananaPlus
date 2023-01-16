import sys
import os
import pathlib
file_id = ".bp"
data_path = os.path.dirname(os.path.realpath(__file__))

workspace_dir = data_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        if file_name.endswith(file_id):
            try:
                with open(data_path + "\\current_workspace.txt", "w") as f:
                    workspace_dir = f.write(os.path.dirname(os.path.abspath(file_name)))
                    f.close()
            except Exception as e:
                workspace_dir = os.path.dirname(os.path.realpath(__file__))

if os.path.exists(data_path + "\\current_workspace.txt"):
    try:
        with open(data_path + "\\current_workspace.txt", "r") as f:
            workspace_dir = f.read()
            f.close()
    except:
        workspace_dir = os.path.dirname(os.path.realpath(__file__))
        
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import Context
from src.symbol_table import SymbolTable
import src.built_in as built_in

global_symbol_table = SymbolTable()

lib_dir = pathlib.Path.home().drive + "\\BananaPlus\\libs"

built_in.register_var(global_symbol_table)

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    
    return result.value, result.error

def import_lib(fn, text, context):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, None, ast.error

    interpreter = Interpreter()

    from src.position import Position

    new_context = Context(f"<Import '{fn}'>", context, Position(-1, 0, -1, fn, text))
    lib_symbol_table = SymbolTable(new_context.parent.symbol_table)



    new_context.symbol_table = lib_symbol_table

    result = interpreter.visit(ast.node, new_context)

    return lib_symbol_table, result.value, result.error

# run file
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        if file_name.endswith(file_id):
            try:
                with open(file_name, "r") as f:
                    script = f.read()

                vlaue, error = run(file_name, script)
                if error: print(error.as_string())
            except Exception as e:
                print(e)