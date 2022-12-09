from src.token import Token
from src.position import Position
from src.rt_types import *
from src.errors import IllegalCharError, ExpectedCharError, Context, InvalidSyntaxError
from src.parser import Parser
from src.interpreter import Interpreter

from src.types import String

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == "/":
                token, error = self.make_slash()
                if error: return [], error
                if token != None:
                    tokens.append(token)
            elif self.current_char in ";\n":
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char in ('"', "'"):
                tokens.append(self.make_string())
            
            #! f string nor working right now
            # elif self.current_char == "`":
            #     token, error = self.make_f_string()
            #     if error: return [], error
            #     tokens.append(token)
            
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(TT_LCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == ":":
                tokens.append(Token(TT_COLON, pos_start=self.pos))
                self.advance()
            elif self.current_char == ".":
                tokens.append(Token(TT_DOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == "!":
                tok, error = self.make_not_equals()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def skip_comment(self):
        self.advance()

        while self.current_char != '\n':
            self.advance()

        self.advance()

    def make_slash(self):
        pos_start = self.pos.copy()

        self.advance()

        if self.current_char == "/":
            self.skip_comment()
            return None, None
        
        return None, IllegalCharError(pos_start, self.pos, "'" + self.current_char + "'")

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False

        started_quote = self.current_char

        self.advance()

        while self.current_char != None and (self.current_char != started_quote or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == "\\":
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()

        self.advance()

        return Token(TT_STRING, string, pos_start, self.pos)
    
    #! not working right now
    def make_f_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        start_code = False
        in_code = False
        code = ''
        pos_start = self.pos.copy()

        self.advance()

        while self.current_char != None and (self.current_char != '`' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            elif start_code:
                if self.current_char == "{":
                    in_code = True
                    start_code = False
                    pos_start = self.pos.copy()
                    pos_start.col -= 1
                else:
                    string += "$"
            elif in_code:
                if self.current_char == "}":
                    if len(code) > 0:
                        lexer = Lexer(self.fn, code)
                        tokens, error = lexer.make_tokens()
                        if error: 
                            old_pos_start = error.pos_start
                            error.pos_start = pos_start
                            error.pos_start.col += 2 + old_pos_start.col
                            error.pos_end.col = self.pos.col
                            error.pos_start.ftxt = self.pos.ftxt 
                            return None, error

                        parser = Parser(tokens)
                        ast = parser.parse()
                        if ast.error:
                            old_pos_start = ast.error.pos_start
                            ast.error.pos_start = pos_start
                            ast.error.pos_start.col += 2 + old_pos_start.col
                            ast.error.pos_end.col = self.pos.col
                            ast.error.pos_start.ftxt = self.pos.ftxt 
                            return None, ast.error

                        interpreter = Interpreter()
                        context = Context('String')

                        from BananaLang import global_symbol_table

                        context.symbol_table = global_symbol_table
                        result = interpreter.visit(ast.node, context)

                        if result.error:
                            old_pos_start = result.error.pos_start
                            result.error.pos_start = pos_start
                            result.error.pos_start.col += 2 + old_pos_start.col
                            result.error.pos_end.col = self.pos.col
                            result.error.pos_start.ftxt = self.pos.ftxt 
                            return None, result.error

                        if isinstance(result.value, String):
                            string += result.value.value
                        else:
                            string += "".join([str(i) for i in result.value.elements]) 
                    in_code = False
                    code = ''
                else:
                    code += self.current_char
            else:
                if self.current_char == "\\":
                    escape_character = True
                elif self.current_char == "$":
                    start_code = True
                else:
                    string += self.current_char
            self.advance()

        if start_code: string += "$"
        if in_code: return None, InvalidSyntaxError(pos_start, self.pos.copy(), "Expected '}'")

        self.advance()

        return Token(TT_STRING, string, pos_start, self.pos), None

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS_LIST else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TT_EE
        elif self.current_char == ">":
            self.advance()
            tok_type = TT_ARROW


        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)