from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import Context
from src.symbol_table import SymbolTable
import src.types as types

global_symbol_table = SymbolTable()

types.register_var(global_symbol_table)

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # print(ast.node.element_nodes[0])

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    
    return result.value, result.error