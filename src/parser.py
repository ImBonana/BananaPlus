from src.errors import InvalidSyntaxError
from src.rt_types import *
from src.nodes import *
from src.results import ParseResult

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1

        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def deadvance(self, ignore_newline=False):
        self.tok_idx -= 1
        self.update_current_tok()
        if self.current_tok.type == TT_NEWLINE and ignore_newline:
            return self.deadvance()
        return self.current_tok

    def skip_newline(self, res=None):
        while self.current_tok.type == TT_NEWLINE:
            if res: res.register_advancement()
            self.advance()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type not in (TT_EOF, TT_KEYWORD, TT_DOT):
            self.deadvance()

            if self.current_tok.matches(TT_KEYWORD, KEYWORDS.AS):
                self.advance()
                if self.current_tok.type == TT_IDENTIFIER:
                    return res
                self.deadvance()

            self.advance()
            
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '.', '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', '{KEYWORDS.AND}' or '{KEYWORDS.OR}'"))
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            if self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                return res.success(ListNode(
                    statements,
                    pos_start,
                    self.current_tok.pos_end.copy()
                ))

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(ListNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.RETURN):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())

            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.CONTINUE):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
        
        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.BREAK):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.RETURN}', '{KEYWORDS.CONTINUE}', '{KEYWORDS.BREAK}', '{KEYWORDS.VAR}', '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}' 'int, float, boolean, identifier, '+', '-', '(', '{'{'}', '[' or '{KEYWORDS.NOT}'"
            ))

        return res.success(expr)

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.FUNCTION):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.FUNCTION}'"
            ))

        isPublic = self.isPublic()

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '('"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or '('"
                ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        self.skip_newline(res)

        if self.current_tok.type == TT_IDENTIFIER:
            onlyOptional = False

            tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_QM:
                onlyOptional = True
                arg_name_toks.append((tok, True))
                res.register_advancement()
                self.advance()
            else:
                arg_name_toks.append((tok, False))
            
            self.skip_newline(res)
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                self.skip_newline(res)
                
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected identifier"
                    ))

                tok = self.current_tok

                res.register_advancement()
                self.advance()
                 
                if onlyOptional and self.current_tok.type != TT_QM:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Optional arguments can only be at the end"
                    ))
                
                if self.current_tok.type == TT_QM: 
                    onlyOptional = True
                    arg_name_toks.append((tok, True))
                    res.register_advancement()
                    self.advance()
                else:
                    arg_name_toks.append((tok, False))
                

                self.skip_newline(res)

            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or ')'"
                ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_ARROW:
            res.register_advancement()
            self.advance()
            body = res.register(self.expr())
            if res.error: return res

            return res.success(FuncDefNode(
                var_name_tok,
                arg_name_toks,
                body,
                True,
                isPublic,
                var_name_tok.pos_start if var_name_tok else arg_name_toks[0].pos_start if len(arg_name_toks) > 0 else body.pos_start,
                body.pos_end
            ))

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '=>' or new line"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.END}'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(
            var_name_tok,
            arg_name_toks,
            body,
            False,
            isPublic,
            var_name_tok.pos_start if var_name_tok else arg_name_toks[0].pos_start if len(arg_name_toks) > 0 else body.pos_start,
            body.pos_end
        ))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases(KEYWORDS.IF))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(
            cases,
            else_case,
            cases[0][0].pos_start,
            (else_case or cases[len(cases) - 1])[0].pos_end
        ))

    def if_expr_b(self):
        return self.if_expr_cases(KEYWORDS.ELIF)

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.ELSE):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected '{KEYWORDS.END}'"
                    ))
            else:
                expr = res.register(self.expr())
                if res.error: return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.ELIF):
            all_cases = res.register(self.if_expr_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        self.skip_newline(res)

        condition = res.register(self.expr())
        if res.error: return res

        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.THEN}'"
            ))

        res.register_advancement()
        self.advance()
        
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.FOR):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.FOR}'"
            ))

        res.register_advancement()
        self.advance()

        self.skip_newline(res)

        if self.current_tok.type == TT_IDENTIFIER:
            for_count_expr = res.register(self.for_count_expr())
            if res.error: return res
            return res.success(for_count_expr)
        elif self.current_tok.matches(TT_KEYWORD, KEYWORDS.FOR_OBJECT):
            for_object_expr = res.register(self.for_object_expr())
            if res.error: return res
            return res.success(for_object_expr)
        elif self.current_tok.matches(TT_KEYWORD, KEYWORDS.FOR_LIST):
            for_list_expr = res.register(self.for_list_expr())
            if res.error: return res
            return res.success(for_list_expr)
        
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier, '{KEYWORDS.FOR_OBJECT}', '{KEYWORDS.FOR_LIST}'"
        ))

    def for_count_expr(self):
        res = ParseResult()

        var_name = self.current_tok

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '='"
            ))

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        start_value = res.register(self.expr())
        if res.error: return res

        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.TO):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.TO}'"
            ))


        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        end_value = res.register(self.expr())
        if res.error: return res
        
        self.skip_newline(res)

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.STEP):
            res.register_advancement()
            self.advance()

            self.skip_newline(res)

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.THEN}'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{KEYWORDS.END}'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(ForNode(
                var_name,
                start_value,
                end_value,
                step_value,
                body,
                True,
                var_name.pos_start,
                body.pos_end
            ))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForNode(
            var_name,
            start_value,
            end_value,
            step_value,
            body,
            False,
            var_name.pos_start,
            body.pos_end
        ))

    def for_object_expr(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))

        key_var_name_tok = self.current_tok

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if self.current_tok.type != TT_COMMA:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ','"
            ))

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))

        value_var_name_tok = self.current_tok

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.IN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.IN}'"
            ))

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        object_tok = res.register(self.expr())
        if res.error: return res

        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.THEN}'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{KEYWORDS.END}'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(ForObjectNode(
                key_var_name_tok,
                value_var_name_tok,
                object_tok,
                body,
                True,
                pos_start,
                self.current_tok.pos_end.copy()
            ))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForObjectNode(
            key_var_name_tok,
            value_var_name_tok,
            object_tok,
            body,
            False,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def for_list_expr(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))

        var_name_tok = self.current_tok

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.IN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.IN}'"
            ))

        res.register_advancement()
        self.advance()
        self.skip_newline(res)

        list_tok = res.register(self.expr())
        if res.error: return res

        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.THEN}'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{KEYWORDS.END}'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(ForListNode(
                var_name_tok,
                list_tok,
                body,
                True,
                pos_start,
                self.current_tok.pos_end.copy()
            ))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForListNode(
            var_name_tok,
            list_tok,
            body,
            False,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.WHILE):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.WHILE}'"
            ))

        self.skip_newline(res)

        res.register_advancement()
        self.advance()

        self.skip_newline(res)

        condition = res.register(self.expr())
        if res.error: return res

        self.skip_newline(res)

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.THEN}'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{KEYWORDS.END}'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(
                condition,
                body,
                True,
                condition.pos_start,
                body.pos_end
            ))

        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(
            condition,
            body,
            False,
            condition.pos_start,
            body.pos_end
        ))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        self.skip_newline(res)
        
        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ']', '{KEYWORDS.VAR}', '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}', int, float, list, boolean, null, identifier, '+', '-', '(', '{'{'}' or '['"
                ))

            self.skip_newline(res)

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                self.skip_newline(res)

                element_nodes.append(res.register(self.expr()))
                if res.error: return res

                self.skip_newline(res)
            
            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))
            
            res.register_advancement()
            self.advance()

        return res.success(
            ListNode(
                element_nodes,
                pos_start,
                self.current_tok.pos_end.copy()
            )
        )
    
    def object_expr(self):
        res = ParseResult()
        elements_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        self.skip_newline(res)

        if self.current_tok.type == TT_RCURLY:
            res.register_advancement()
            self.advance()
        else:
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))

            var_name = self.current_tok

            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_COLON:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ':'"
                ))

            res.register_advancement()
            self.advance()

            self.skip_newline(res)

            expr = res.register(self.expr())
            if res.error: 
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{'}'}', '{KEYWORDS.VAR}', '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}', int, float, list, boolean, null, identifier, '+', '-', '(', '{'{'}' or '['"
                ))
            
            elements_nodes.append((var_name, expr))
            
            self.skip_newline(res)

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                self.skip_newline(res)

                if self.current_tok.type == TT_IDENTIFIER:
                    var_name = self.current_tok

                    res.register_advancement()
                    self.advance()

                    if self.current_tok.type != TT_COLON:
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            "Expected ':'"
                        ))

                    res.register_advancement()
                    self.advance()

                    self.skip_newline(res)

                    expr = res.register(self.expr())
                    if res.error: return res
                    elements_nodes.append((var_name, expr))

                    self.skip_newline(res)

            if self.current_tok.type != TT_RCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or '{'}'}'"
                ))
        
            res.register_advancement()
            self.advance()
        
        return res.success(ObjectNode(
                elements_nodes,
                pos_start,
                self.current_tok.pos_end.copy()
            )
        )
    
    def identifier_expr(self):
        res = ParseResult()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))
        
        var_name = self.current_tok

        res.register_advancement()
        self.advance()
        if self.current_tok.type in (TT_EQ, TT_PE, TT_ME):
            var_assign_type = self.current_tok.type
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(
                var_name,
                expr,
                var_assign_type,
                False,
                True,
                var_name.pos_start,
                expr.pos_end
            ))
        elif self.current_tok.type == TT_DOT:
            advance_count = 0
            var_names = []

            var_names.append((var_name, self.current_tok.pos_start, self.current_tok.pos_end))

            while self.current_tok.type == TT_DOT:
                res.register_advancement()
                self.advance()
                advance_count += 1

                if self.current_tok.type != TT_IDENTIFIER and self.current_tok.type != TT_STRING:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected identifier, string"
                    ))

                var_names.append((self.current_tok, self.current_tok.pos_start, self.current_tok.pos_end))

                res.register_advancement()
                self.advance()
                advance_count += 1
            
            if self.current_tok.type in (TT_EQ, TT_PE, TT_ME):
                var_assign_type = self.current_tok.type
                res.register_advancement()
                self.advance()

                expr = res.register(self.expr())
                if res.error: return res
                return res.success(MultiVarAssignNode(
                    var_names,
                    expr,
                    var_assign_type,
                    var_names[0][1],
                    expr.pos_end
                ))
            else:
                for i in range(advance_count):
                    res.register_deadvancement()
                    self.deadvance()
            
        return res.success(VarAccessNode(
            var_name,
            var_name.pos_start,
            var_name.pos_end
        ))

    def import_expr(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.IMPORT):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.IMPORT}'"
            ))
        
        res.register_advancement()
        self.advance()

        lib_name = res.register(self.expr())        
        if res.error: return res

        self.skip_newline(res)
        
        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.AS):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.AS}'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))
        
        var_name = self.current_tok

        res.register_advancement()
        self.advance()

        return res.success(ImportNode(lib_name, var_name, pos_start, self.current_tok.pos_end.copy()))

    def switch_expr(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.SWITCH):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.SWITCH}'"
            ))
        
        res.register_advancement()
        self.advance()

        self.skip_newline(res)

        value_node = res.register(self.expr())        
        if res.error: return res

        self.skip_newline(res)
        
        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.THEN}'"
            ))
        
        res.register_advancement()
        self.advance()

        self.skip_newline(res)

        cases = []
        default = None

        while self.current_tok.matches(TT_KEYWORD, KEYWORDS.CASE):
            res.register_advancement()
            self.advance()
            self.skip_newline(res)

            case_value_node = res.register(self.expr())
            if res.error: return res

            self.skip_newline(res)

            if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.THEN):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{KEYWORDS.THEN}'"
                ))

            res.register_advancement()
            self.advance()
            self.skip_newline(res)

            expr = res.register(self.statements())
            if res.error: return res

            self.skip_newline(res)

            if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '{KEYWORDS.END}'"
                ))

            cases.append((case_value_node, expr))

            res.register_advancement()
            self.advance()
            self.skip_newline(res)


            if self.current_tok.matches(TT_KEYWORD, KEYWORDS.DEFAULT):
                if default != None:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Unexpected '{KEYWORDS.DEFAULT}'"
                    ))

                res.register_advancement()
                self.advance()
                self.skip_newline(res)

                expr = res.register(self.expr())
                if res.error: return res

                self.skip_newline(res)

                if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected '{KEYWORDS.END}'"
                    ))
                
                res.register_advancement()
                self.advance()
                self.skip_newline(res)

                default = expr

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.END):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.END}'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(SwitchNode(value_node, cases, default, pos_start, self.current_tok.pos_end.copy()))

    def private_and_public_expr(self):
        res = ParseResult()
        
        res.register_advancement()
        self.advance()

        if not self.current_tok.matches(TT_KEYWORD, KEYWORDS.VAR) and not self.current_tok.matches(TT_KEYWORD, KEYWORDS.FUNCTION):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.VAR}' or '{KEYWORDS.FUNCTION}'"
            ))
            
        expr = res.register(self.expr())
        if res.error: return res

        return res.success(expr)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok, tok.pos_start, tok.pos_end))
        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok, tok.pos_start, tok.pos_end))
        elif tok.matches(TT_KEYWORD, KEYWORDS.NULL):
            res.register_advancement()
            self.advance()
            return res.success(NullNode(tok.pos_start, tok.pos_end))
        elif tok.matches(TT_KEYWORD, KEYWORDS.TRUE):
            res.register_advancement()
            self.advance()
            return res.success(BooleanNode(True, tok.pos_start, tok.pos_end))
        elif tok.matches(TT_KEYWORD, KEYWORDS.FALSE):
            res.register_advancement()
            self.advance()
            return res.success(BooleanNode(False, tok.pos_start, tok.pos_end))
        elif tok.type == TT_IDENTIFIER:
            identifier_expr = res.register(self.identifier_expr())
            if res.error: return res
            return res.success(identifier_expr)
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            self.skip_newline(res)
            expr = res.register(self.expr())
            if res.error: return res
            self.skip_newline(res)
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected ')'"))
        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)
        elif tok.type == TT_LCURLY:
            object_expr = res.register(self.object_expr())
            if res.error: return res
            return res.success(object_expr)
        elif tok.matches(TT_KEYWORD, KEYWORDS.IF):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)
        elif tok.matches(TT_KEYWORD, KEYWORDS.FOR):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        elif tok.matches(TT_KEYWORD, KEYWORDS.WHILE):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        elif tok.matches(TT_KEYWORD, KEYWORDS.FUNCTION):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)
        elif tok.matches(TT_KEYWORD, KEYWORDS.IMPORT):
            import_expr = res.register(self.import_expr())
            if res.error: return res
            return res.success(import_expr)
        elif tok.matches(TT_KEYWORD, KEYWORDS.SWITCH):
            switch_expr = res.register(self.switch_expr())
            if res.error: return res
            return res.success(switch_expr)
        elif tok.matches(TT_KEYWORD, KEYWORDS.PRIVATE) or tok.matches(TT_KEYWORD, KEYWORDS.PUBLIC):
            private_and_public_expr = res.register(self.private_and_public_expr())
            if res.error: return res
            return res.success(private_and_public_expr)

        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, f"Expected '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}', int, float, list, boolean, null, identifier, '+', '-', '(', '{'{'}' or '['"))
    
    def dot(self):
        return self.bin_op(self.atom, (TT_DOT, ))

    def call(self):
        res = ParseResult()
        dot = res.register(self.dot())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            self.skip_newline(res)
            arg_nodes = []
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                self.skip_newline(res)
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ')', '{KEYWORDS.VAR}', '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}', int, float, list, boolean, null, identifier, '+', '-' or '('"
                    ))
                self.skip_newline(res)
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    self.skip_newline(res)

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                    self.skip_newline(res)
                
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))
                
                res.register_advancement()
                self.advance()
                
            return res.success(CallNode(
                dot,
                arg_nodes,
                dot.pos_start,
                arg_nodes[len(arg_nodes) - 1].pos_end if len(arg_nodes) > 0 else dot.pos_end               
            ))
        return res.success(dot)

    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(
                tok,
                factor,
                tok.pos_start,
                factor.pos_end
            ))
        
        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.NOT):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(
                op_tok,
                node,
                op_tok.pos_start,
                node.pos_end
            ))

        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}', int, float, list, boolean, null, identifier, '+', '-', '(', '{'{'}', '[' or '{KEYWORDS.NOT}'"))

        return res.success(node)

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.VAR):
            isPublic = self.isPublic()
            res.register_advancement()
            self.advance()

            self.skip_newline(res)

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            self.skip_newline(res)

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))

            res.register_advancement()
            self.advance()
            self.skip_newline(res)
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(
                var_name,
                expr,
                TT_EQ,
                isPublic,
                False,
                var_name.pos_start,
                expr.pos_end
            ))

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, KEYWORDS.AND), (TT_KEYWORD, KEYWORDS.OR))))
        if res.error: 
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{KEYWORDS.VAR}', '{KEYWORDS.IF}', '{KEYWORDS.FOR}', '{KEYWORDS.WHILE}', '{KEYWORDS.FUNCTION}' 'int, float, boolean, identifier, '+', '-', '(', '{'{'}', '[' or '{KEYWORDS.NOT}'"
            ))

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            self.skip_newline(res)
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(
                left,
                op_tok,
                right,
                left.pos_start,
                right.pos_end
            )

        return res.success(left)
    
    def isPublic(self):
        self.deadvance()

        if self.current_tok.matches(TT_KEYWORD, KEYWORDS.PUBLIC):
            self.advance()
            return True
        elif self.current_tok.matches(TT_KEYWORD, KEYWORDS.PRIVATE):
            self.advance()
            return False
        self.advance()
        return False