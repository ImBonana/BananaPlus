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
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LSQUARE = "LSQUARE"
TT_RSQUARE = "RSQUARE"
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

class keyWordsClass:
    def __init__(self):
        self.VAR = "VAR"
        self.FALSE = "false"
        self.TRUE = "true"
        self.NULL = "null"
        self.AND = "AND"
        self.OR = "OR"
        self.NOT = "NOT"
        self.IF = "IF"
        self.THEN = "THEN"
        self.ELIF = "ELIF"
        self.ELSE = "ELSE"
        self.FOR = "FOR"
        self.TO = "TO"
        self.STEP = "STEP"
        self.WHILE = "WHILE"
        self.FUNCTION = "FUNC"
        self.END = "END"
        self.RETURN = "RETURN"
        self.CONTINUE = "CONTINUE"
        self.BREAK = "BREAK"

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
    KEYWORDS.BREAK
]