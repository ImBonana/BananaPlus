from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import Context
from src.symbol_table import SymbolTable
from src.types import Null

global_symbol_table = SymbolTable()

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
    
    # if isinstance(result.value, Null):
    #     return "null", result.error
    return result.value, result.error