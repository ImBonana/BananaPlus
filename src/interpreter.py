from src.types import Number, Boolean, Null, Function, String, List, Object
from src.results import RTResult
from src.rt_types import *
from src.errors import RTError

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_StringNode(self, node, context):
        return RTResult().success(String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BooleanNode(self, node, context):
        return RTResult().success(Boolean(node.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_NullNode(self, node, context):
        return RTResult().success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return(): return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ObjectNode(self, node, context):
        res = RTResult()
        elements = {}

        for element in node.element_nodes:
            elements[element[0].value] = res.register(self.visit(element[1], context))
            if res.should_return(): return res

        return res.success(
            Object(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(
                RTError(
                    node.pos_start, node.pos_end,
                    f"'{var_name}' is not defined",
                    context
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        update = node.update

        if update:
            u_value = context.symbol_table.get(var_name)
            
            if not u_value:
                return res.failure(
                    RTError(
                        node.pos_start, node.pos_end,
                        f"'{var_name}' is not defined",
                        context
                    )
                )

        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_MultiVarAccessNode(self, node, context):
        res = RTResult()
        var_names = node.var_name_toks

        current_value = None

        for var_name in var_names:

            if current_value == None:
                value = context.symbol_table.get(var_name[0].value)
            else:
                if isinstance(current_value, Object):
                    value = current_value.elements.get(var_name[0].value, None)
                else:
                    value = current_value.built_in.get(var_name[0].value, None)

            if value == None:
                return res.failure(
                    RTError(
                        var_name[1], var_name[2],
                        f"'{var_name[0].value}' is not defined",
                        context
                    )
                )
            
            current_value = value

        current_value = current_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(current_value)

    def visit_MultiVarAssignNode(self, node, context):
        res = RTResult()
        var_names = node.var_name_toks

        current_value = None
        i = 0
        for var_name in var_names:
            i += 1
            if current_value == None:
                value = context.symbol_table.get(var_name[0].value)

                if not isinstance(value, Object):
                    return res.failure(
                        RTError(
                            node.pos_start, node.pos_end,
                            f"'{current_value}' is not a object",
                            context
                        )
                    )
            else:
                value = current_value.elements.get(var_name[0].value, None)

            if not value:
                return res.failure(
                    RTError(
                        var_name[1], var_name[2],
                        f"'{var_name[0].value}' is not defined",
                        context
                    )
                )
            
            current_value = value

            if len(var_names)-1 == i:
                try:
                    current_value.elements[var_names[len(var_names)-1][0].value] = res.register(self.visit(node.value_node, context))
                except:
                    return res.failure(
                    RTError(
                        var_name[1], var_name[2],
                        f"'{current_value}' is not a object",
                        context
                    )
                )

        return res.success(context.symbol_table.get(var_names[0][0].value))

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res

        if node.op_tok.type == TT_DOT:
            result, error = left.dotted_to(right)
        elif node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, KEYWORDS.AND):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, KEYWORDS.OR):
            result, error = left.ored_by(right)

        if error: 
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, KEYWORDS.NOT):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res
            
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(Null() if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context))
            if res.should_return(): return res
            return res.success(Null() if should_return_null else expr_value)

        return res.success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return(): return res

        if not isinstance(start_value, Number):
                return res.failure(RTError(
                    start_value.pos_start, start_value.pos_end,
                    "Expected number",
                    context
                ))

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return(): return res

        if not isinstance(end_value, Number):
                return res.failure(RTError(
                    end_value.pos_start, end_value.pos_end,
                    "Expected number",
                    context
                ))

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return(): return res

            if not isinstance(step_value, Number):
                return res.failure(RTError(
                    step_value.pos_start, step_value.pos_end,
                    "Expected number",
                    context
                ))
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Null() if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true(): break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Null() if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        func_value = Function(func_name, body_node, node.arg_name_toks, node.should_auto_return).set_context(context).set_pos()

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)
    
    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)

    def visit_ImportNode(self, node, context):
        res = RTResult()

        lib_name = res.register(self.visit(node.lib_name, context))
        if res.should_return(): return res

        if not isinstance(lib_name, String):
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                "Lib name must be string",
                context
            ))

        var_name = node.var_name.value

        if not var_name:
            return RTResult().failure(RTError(
                var_name.pos_start, var_name.pos_end,
                "Expected identfier",
                context
            ))

        lib_name = lib_name.value

        path = lib_name

        from BananaLang import workspace_dir, lib_dir

        if lib_name.endswith(".bl"):
            path = workspace_dir
            path += "\\"
            path += lib_name
        else:
            path = lib_dir
            path += "\\"
            path += lib_name + ".bl"

        try:
            with open(path, "r") as f:
                script = f.read()
        except Exception as e:
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                F"Failed to load script \"{path}\"\n" + str(e),
                context
            ))
        
        from BananaLang import import_lib

        vars, result, error = import_lib(lib_name, script)

        if error:
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                f"Failed to finish executing script \"{path}\"\n" + error.as_string(),
                context
            ))

        context.symbol_table.set(var_name, Object(vars))

        return RTResult().success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Null()

        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()
    
    def visit_BreakNode(self, node, context):
        return RTResult().success_break()