import re

# Типы токенов
TOKEN_EOF = -1
TOKEN_NUMBER = -2
TOKEN_IDENTIFIER = -3
TOKEN_INT = -4
TOKEN_DOUBLE = -5
TOKEN_BOOL = -6
TOKEN_TRUE = -7
TOKEN_FALSE = -8
TOKEN_PLUS = ord('+')
TOKEN_MINUS = ord('-')
TOKEN_MULTIPLY = ord('*')
TOKEN_DIVIDE = ord('/')
TOKEN_LPAREN = ord('(')
TOKEN_RPAREN = ord(')')
TOKEN_SEMI = ord(';')
TOKEN_EQ = -9
TOKEN_NE = -10
TOKEN_LT = -11
TOKEN_LE = -12
TOKEN_GT = -13
TOKEN_GE = -14
TOKEN_AND = -15
TOKEN_OR = -16
TOKEN_IF = -17
TOKEN_ELSE = -18
TOKEN_ASSIGN = ord('=')
TOKEN_WHILE = -19
TOKEN_PRINT = -20
TOKEN_ENDL = -21
TOKEN_STRING = -22
TOKEN_LBRACE = ord('{')
TOKEN_RBRACE = ord('}')
TOKEN_LSQUARE = ord('[')
TOKEN_RSQUARE = ord(']')
TOKEN_COMMA = ord(',')
TOKEN_INPUT = -23
TOKEN_COMMENT = -24

# Лексер
class Lexer:
    def __init__(self, input_stream):
        self.input_stream = input_stream
        self.last_char = ' '
        self.identifier_str = ''
        self.num_val = 0
        self.string_val = ''
        self.bool_val = False

    def gettok(self):
        while self.last_char.isspace():
            self.last_char = self.input_stream.read(1)
            if not self.last_char:
                return TOKEN_EOF

        if self.last_char == '#':
            while self.last_char not in ('\n', '\r', ''):
                self.last_char = self.input_stream.read(1)
            if self.last_char:
                return self.gettok()

        if re.match(r'[a-zA-Zа-яА-Я]', self.last_char):
            self.identifier_str = self.last_char
            while True:
                self.last_char = self.input_stream.read(1)
                if not re.match(r'[a-zA-Z0-9а-яА-Я_]', self.last_char):
                    break
                self.identifier_str += self.last_char
            if self.identifier_str == "цел":
                return TOKEN_INT
            if self.identifier_str == "вещ":
                return TOKEN_DOUBLE
            if self.identifier_str == "бул":
                return TOKEN_BOOL
            if self.identifier_str == "если":
                return TOKEN_IF
            if self.identifier_str == "иначе":
                return TOKEN_ELSE
            if self.identifier_str == "true":
                self.bool_val = True
                return TOKEN_TRUE
            if self.identifier_str == "false":
                self.bool_val = False
                return TOKEN_FALSE
            if self.identifier_str == "нц_пока":
                return TOKEN_WHILE
            if self.identifier_str == "вывод":
                return TOKEN_PRINT
            if self.identifier_str == "конецстр":
                return TOKEN_ENDL
            if self.identifier_str == "ввод":
                return TOKEN_INPUT
            return TOKEN_IDENTIFIER

        if re.match(r'\d|\.', self.last_char):
            num_str = ''
            while re.match(r'\d|\.', self.last_char):
                num_str += self.last_char
                self.last_char = self.input_stream.read(1)
            self.num_val = float(num_str)
            return TOKEN_NUMBER

        if self.last_char == '\"':
            self.string_val = ''
            self.last_char = self.input_stream.read(1)
            while self.last_char != '\"' and self.last_char:
                self.string_val += self.last_char
                self.last_char = self.input_stream.read(1)
            self.last_char = self.input_stream.read(1)
            return TOKEN_STRING

        if not self.last_char:
            return TOKEN_EOF

        if self.last_char == '=':
            self.last_char = self.input_stream.read(1)
            if self.last_char == '=':
                self.last_char = self.input_stream.read(1)
                return TOKEN_EQ
            return TOKEN_ASSIGN

        if self.last_char == '!':
            self.last_char = self.input_stream.read(1)
            if self.last_char == '=':
                self.last_char = self.input_stream.read(1)
                return TOKEN_NE

        if self.last_char == '<':
            self.last_char = self.input_stream.read(1)
            if self.last_char == '=':
                self.last_char = self.input_stream.read(1)
                return TOKEN_LE
            return TOKEN_LT

        if self.last_char == '>':
            self.last_char = self.input_stream.read(1)
            if self.last_char == '=':
                self.last_char = self.input_stream.read(1)
                return TOKEN_GE
            return TOKEN_GT

        if self.last_char == '&':
            self.last_char = self.input_stream.read(1)
            if self.last_char == '&':
                self.last_char = self.input_stream.read(1)
                return TOKEN_AND

        if self.last_char == '|':
            self.last_char = self.input_stream.read(1)
            if self.last_char == '|':
                self.last_char = self.input_stream.read(1)
                return TOKEN_OR
    
        this_char = self.last_char
        self.last_char = self.input_stream.read(1)

        res = ord(this_char) if this_char in '+-*/(){}[],' else {
            '=': TOKEN_ASSIGN,
            ';': TOKEN_SEMI,
            '<': TOKEN_LT,
            '>': TOKEN_GT,
            '!': TOKEN_NE,
            '&': TOKEN_AND,
            '|': TOKEN_OR
        }.get(this_char, ord(this_char))

        # print("gettok: ", res, this_char)
        return res