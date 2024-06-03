import sys
from lexer import *

class ExprAST:
    def evaluate(self):
        raise NotImplementedError

class NumberExprAST(ExprAST):
    def __init__(self, val):
        self.val = val

    def evaluate(self):
        return self.val

class BooleanExprAST(ExprAST):
    def __init__(self, val):
        self.val = val

    def evaluate(self):
        return True if self.val else False

class StringExprAST(ExprAST):
    def __init__(self, val):
        self.val = val

    def evaluate(self):
        print(self.val, end='')
        return ""
class VariableExprAST(ExprAST):
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        if self.name in named_values:
            var = named_values[self.name]
            if var['type'] == 'array':
                raise RuntimeError(f"Array {self.name} used without index")
            return var['value']
        raise RuntimeError(f"Unknown variable name: {self.name}")

class BinaryExprAST(ExprAST):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        # print("binary op:", self.op, chr(45))

    def evaluate(self):
        left_val = self.lhs.evaluate()
        right_val = self.rhs.evaluate()
        
        if self.op == ord('/'):
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
        # print(left_val, right_val, self.op)
        if self.op == ord('/'):
            return left_val / right_val
        res = {
            ord('+'): left_val + right_val,
            ord('-'): left_val - right_val,
            ord('*'): left_val * right_val,
            TOKEN_EQ: left_val == right_val,
            TOKEN_NE: left_val != right_val,
            TOKEN_LT: left_val < right_val,
            TOKEN_LE: left_val <= right_val,
            TOKEN_GT: left_val > right_val,
            TOKEN_GE: left_val >= right_val,
            TOKEN_AND: left_val and right_val,
            TOKEN_OR: left_val or right_val,
        }[self.op]
        return res

class IfExprAST(ExprAST):
    def __init__(self, cond, then_expr, else_expr):
        self.cond = cond
        self.then_expr = then_expr
        self.else_expr = else_expr

    def evaluate(self):
        if self.cond.evaluate():
            return self.then_expr.evaluate()
        elif self.else_expr:
            return self.else_expr.evaluate()
        return 0.0

class BlockExprAST(ExprAST):
    def __init__(self, expressions):
        self.expressions = expressions

    def evaluate(self):
        result = 0.0
        for expr in self.expressions:
            result = expr.evaluate()
        return result
    
class ArrayExprAST(ExprAST):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    def evaluate(self):
        if self.name in named_values:
            if named_values[self.name]['type'] == 'array':
                idx = int(self.index.evaluate())
                array = named_values[self.name]['value']
                if 0 <= idx < len(array):
                    return array[idx]
                else:
                    raise IndexError("Array index out of bounds")
        raise RuntimeError(f"Unknown array name: {self.name}")
    
class ArrayDeclarationExprAST(ExprAST):
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def evaluate(self):
        named_values[self.name] = {'type': 'array', 'value': [0] * self.size}
        return 0.0

class VariableAssignmentExprAST(ExprAST):
    def __init__(self, name, expr, index=None):
        self.name = name
        self.expr = expr
        self.index = index

    def evaluate(self):
        val = self.expr.evaluate()
        if self.index:  # Это массив
            if self.name in named_values and named_values[self.name]['type'] == 'array':
                idx = int(self.index.evaluate())
                array = named_values[self.name]['value']
                if 0 <= idx < len(array):
                    array[idx] = val
                else:
                    raise IndexError("Array index out of bounds")
            else:
                raise RuntimeError(f"Unknown array name: {self.name}")
        else:  # Это обычная переменная
            if self.name in named_values:
                named_values[self.name]['value'] = val
            else:
                raise RuntimeError(f"Unknown variable name: {self.name}")
        return val


class VariableDeclarationExprAST(ExprAST):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def evaluate(self):
        val = self.expr.evaluate()
        named_values[self.name] = {'type': 'double', 'value': val}
        return val

class WhileExprAST(ExprAST):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def evaluate(self):
        result = 0.0
        while self.cond.evaluate():
            result = self.body.evaluate()
        return result

class PrintExprAST(ExprAST):
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self):
        result = self.expr.evaluate()
        # print("result: ", result)
        print(result, end='')
        return result

class EndlExprAST(ExprAST):
    def evaluate(self):
        print()
        return 0.0

class InputExprAST(ExprAST):
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        if self.name in named_values:
            val = float(input())
            named_values[self.name]['value'] = val
            return val
        raise RuntimeError(f"Unknown variable name: {self.name}")

# Глобальные переменные
named_values = {}

# Лексер
lexer = None
cur_tok = None

def get_next_token():
    global cur_tok
    cur_tok = lexer.gettok()
    try:
        h = chr(cur_tok)
    except:
        h = cur_tok
    # print("Next token: ", h)
    return cur_tok

def parse_expression():
    lhs = parse_primary()
    if not lhs:
        return None
    return parse_bin_op_rhs(0, lhs)

def parse_number_expr():
    result = NumberExprAST(lexer.num_val)
    get_next_token()
    return result

def parse_boolean_expr():
    result = BooleanExprAST(lexer.bool_val)
    get_next_token()
    return result

def parse_string_expr():
    result = StringExprAST(lexer.string_val)
    get_next_token()
    return result

def parse_paren_expr():
    get_next_token()
    v = parse_expression()
    if not v:
        return None
    # print("tok2", cur_tok)
    if cur_tok != ord(')'):
        return None
    get_next_token()
    return v

def parse_identifier_expr():
    id_name = lexer.identifier_str
    get_next_token()
    if cur_tok == ord('['):
        get_next_token()
        index = parse_expression()
        if cur_tok != ord(']'):
            raise RuntimeError("Expected ']' after array index")
        get_next_token()
        if cur_tok == ord('='):
            get_next_token()
            expr = parse_expression()
            return VariableAssignmentExprAST(id_name, expr, index)
        return ArrayExprAST(id_name, index)
    if cur_tok == ord('='):
        get_next_token()
        expr = parse_expression()
        return VariableAssignmentExprAST(id_name, expr)
    return VariableExprAST(id_name)

def parse_while_expr():
    get_next_token()
    if cur_tok != ord('('):
        return None
    get_next_token()
    cond = parse_expression()
    if not cond:
        return None
    if cur_tok != ord(')'):
        return None
    get_next_token()
    if cur_tok != ord('{'):
        return None
    body = parse_block()
    if not body:
        return None
    return WhileExprAST(cond, body)

def parse_print_expr():
    get_next_token()
    expr = parse_expression()
    if not expr:
        return None
    return PrintExprAST(expr)

def parse_endl_expr():
    get_next_token()
    return EndlExprAST()

def parse_input_expr():
    get_next_token()
    if cur_tok != TOKEN_IDENTIFIER:
        return None
    id_name = lexer.identifier_str
    get_next_token()
    return InputExprAST(id_name)

def parse_primary():
    if cur_tok == TOKEN_IDENTIFIER:
        return parse_identifier_expr()
    if cur_tok == TOKEN_NUMBER:
        return parse_number_expr()
    if cur_tok in (TOKEN_TRUE, TOKEN_FALSE):
        return parse_boolean_expr()
    if cur_tok == TOKEN_STRING:
        return parse_string_expr()
    if cur_tok == ord('('):
        return parse_paren_expr()
    if cur_tok == TOKEN_IF:
        return parse_if_expr()
    if cur_tok == TOKEN_WHILE:
        return parse_while_expr()
    if cur_tok == TOKEN_PRINT:
        return parse_print_expr()
    if cur_tok == TOKEN_ENDL:
        return parse_endl_expr()
    if cur_tok == TOKEN_INPUT:
        return parse_input_expr()
    return None

def get_tok_precedence():
    return {
        ord('+'): 10,
        ord('-'): 10,
        ord('*'): 20,
        ord('/'): 20,
        TOKEN_EQ: 5,
        TOKEN_NE: 5,
        TOKEN_LT: 15,
        TOKEN_LE: 15,
        TOKEN_GT: 15,
        TOKEN_GE: 15,
        TOKEN_AND: 3,
        TOKEN_OR: 1
    }.get(cur_tok, -1)

def parse_bin_op_rhs(expr_prec, lhs):
    while True:
        tok_prec = get_tok_precedence()
        if tok_prec < expr_prec:
            return lhs
        bin_op = cur_tok
        get_next_token()
        rhs = parse_primary()
        if not rhs:
            return None
        next_prec = get_tok_precedence()
        if tok_prec < next_prec:
            rhs = parse_bin_op_rhs(tok_prec + 1, rhs)
            if not rhs:
                return None
        lhs = BinaryExprAST(bin_op, lhs, rhs)

def parse_block():
    get_next_token()
    expressions = []
    while cur_tok != ord('}') and cur_tok != TOKEN_EOF:
        if cur_tok == ord(';'):
            get_next_token()
            continue
        expr = parse_expression()
        if not expr:
            return None
        expressions.append(expr)
        if cur_tok != ord(';'):
            raise RuntimeError("Expected ';' at the end of expression")
        get_next_token()
    if cur_tok != ord('}'):
        raise RuntimeError("Expected '}' at the end of block")
    get_next_token()
    if len(expressions) == 1:
        return expressions[0]
    return BlockExprAST(expressions)

def parse_if_expr():
    get_next_token()
    if cur_tok != ord('('):
        raise RuntimeError("Expected '(' after 'if'")
    get_next_token()
    cond = parse_expression()
    if not cond:
        return None
    if cur_tok != ord(')'):
        raise RuntimeError("Expected ')' after condition")
    get_next_token()
    if cur_tok != ord('{'):
        raise RuntimeError("Expected '{' after 'if'")
    then_expr = parse_block()
    if not then_expr:
        return None
    else_expr = None
    if cur_tok == TOKEN_ELSE:
        get_next_token()
        if cur_tok != ord('{'):
            raise RuntimeError("Expected '{' after 'else'")
        else_expr = parse_block()
        if not else_expr:
            return None
    return IfExprAST(cond, then_expr, else_expr)

def parse_int_decl():
    get_next_token()
    if cur_tok != TOKEN_IDENTIFIER:
        raise RuntimeError("Expected identifier after 'int'")
    id_name = lexer.identifier_str
    get_next_token()
    if cur_tok == ord('['):
        get_next_token()
        if cur_tok != TOKEN_NUMBER:
            raise RuntimeError("Expected number in array declaration")
        array_size = int(lexer.num_val)
        get_next_token()
        if cur_tok != ord(']'):
            raise RuntimeError("Expected ']' after array size")
        get_next_token()
        return ArrayDeclarationExprAST(id_name, array_size)
    if cur_tok != ord('='):
        raise RuntimeError("Expected '=' after identifier")
    get_next_token()
    expr = parse_expression()
    if not expr:
        return None
    return VariableDeclarationExprAST(id_name, expr)

def parse_bool_decl():
    get_next_token()
    if cur_tok != TOKEN_IDENTIFIER:
        raise RuntimeError("Expected identifier after 'bool'")
    id_name = lexer.identifier_str
    get_next_token()
    if cur_tok != ord('='):
        raise RuntimeError("Expected '=' after identifier")
    get_next_token()
    # print("tok", cur_tok)

    expr = parse_expression()
    if not expr:
        return None
    return VariableDeclarationExprAST(id_name, expr)

def handle_file(filename):
    global lexer
    with open(filename, 'r') as file:
        lexer = Lexer(file)
        while True:
            get_next_token()
            if cur_tok == TOKEN_EOF:
                break
            if cur_tok == ord(';'):
                continue
            ast = None
            # print(cur_tok)
            if cur_tok == TOKEN_INT:
                ast = parse_int_decl()
            elif cur_tok == TOKEN_BOOL:
                ast = parse_bool_decl()
            else:
                ast = parse_expression()
            if ast:
                ast.evaluate()
            else:
                raise RuntimeError("Error parsing expression")
            # if cur_tok != ord(';'):
            #     raise RuntimeError("Expected ';' at the end of the expression")

def handle_interactive():
    global lexer
    lexer = Lexer(sys.stdin)
    while True:
        print("Enter an expression: ", end='')
        get_next_token()
        if cur_tok == TOKEN_EOF:
            break
        if cur_tok == ord(';'):
            continue
        ast = None
        if cur_tok == TOKEN_INT:
            ast = parse_int_decl()
        elif cur_tok == TOKEN_BOOL:
            ast = parse_bool_decl()
        else:
            ast = parse_expression()
        if ast:
            print("Result: ", ast.evaluate())
        else:
            raise RuntimeError("Error parsing expression")
        # if cur_tok != ord(';'):
        #     raise RuntimeError("Expected ';' at the end of the expression")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "-f":
        handle_file(sys.argv[2])
    else:
        handle_interactive()
