from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import Context
from src.symbol_table import SymbolTable
import src.types as types
import src.built_in as built_in
import os

global_symbol_table = SymbolTable()

workspace_dir = os.path.dirname(os.path.realpath(__file__))

lib_dir = os.path.dirname(os.path.realpath(__file__))

file_id = ".bp"


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

def import_lib(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, None, ast.error

    interpreter = Interpreter()

    context = Context('<program>')
    lib_symbol_table = SymbolTable()

    built_in.register_var(lib_symbol_table)

    context.symbol_table = lib_symbol_table

    result = interpreter.visit(ast.node, context)

    built_in.unregister_var(lib_symbol_table)

    return lib_symbol_table.symbols, result.value, result.error