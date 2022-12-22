import string

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POW = "POW"
TT_EQ = "EQ"
TT_PE = "PE"
TT_ME = "ME"
TT_COLON = "COLON"
TT_DOT = "DOT"
TT_QM = "QM"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LSQUARE = "LSQUARE"
TT_RSQUARE = "RSQUARE"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_EE = "EE"
TT_NE = "NE"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"
TT_COMMA = "COMMA"
TT_ARROW = "ARROW"
TT_NEWLINE = "NEWLINE"
TT_EOF = "EOF"

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

escape_characters = {
    "n": "\n",
    "t": "\t"
}

char_spaces = " \t"
char_new_lines = ";\n"

class keyWordsClass:
    def __init__(self):
        self.VAR = "let"
        self.FALSE = "false"
        self.TRUE = "true"
        self.NULL = "null"
        self.AND = "and"
        self.OR = "or"
        self.NOT = "not"
        self.IF = "if"
        self.THEN = "then"
        self.ELIF = "elif"
        self.ELSE = "else"
        self.FOR = "for"
        self.TO = "to"
        self.STEP = "step"
        self.WHILE = "while"
        self.FUNCTION = "func"
        self.END = "end"
        self.RETURN = "return"
        self.CONTINUE = "continue"
        self.BREAK = "break"
        self.IMPORT = "import"
        self.AS = "as"
        self.SWITCH = "switch"
        self.CASE = "case"
        self.DEFAULT = "default"
        self.PUBLIC = "public"
        self.PRIVATE = "private"

KEYWORDS = keyWordsClass()

KEYWORDS_LIST = [
    KEYWORDS.VAR,
    KEYWORDS.FALSE,
    KEYWORDS.TRUE,
    KEYWORDS.NULL,
    KEYWORDS.AND,
    KEYWORDS.OR,
    KEYWORDS.NOT,
    KEYWORDS.IF,
    KEYWORDS.THEN,
    KEYWORDS.ELIF,
    KEYWORDS.ELSE,
    KEYWORDS.FOR,
    KEYWORDS.TO,
    KEYWORDS.STEP,
    KEYWORDS.WHILE,
    KEYWORDS.FUNCTION,
    KEYWORDS.END,
    KEYWORDS.RETURN,
    KEYWORDS.CONTINUE,
    KEYWORDS.BREAK,
    KEYWORDS.IMPORT,
    KEYWORDS.AS,
    KEYWORDS.SWITCH,
    KEYWORDS.CASE,
    KEYWORDS.DEFAULT,
    KEYWORDS.PUBLIC,
    KEYWORDS.PRIVATE
]