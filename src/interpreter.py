from src.types import Number, Boolean, Null, Function, String, List, Object
from src.results import RTResult
from src.rt_types import *
from src.errors import RTError

class Interpreter:
    def visit(self, node, context, bin_op_right=False):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context, bin_op_right)

    def no_visit_method(self, node, context, bin_op_right=False):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context, bin_op_right=False):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_StringNode(self, node, context, bin_op_right=False):
        return RTResult().success(String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BooleanNode(self, node, context, bin_op_right=False):
        return RTResult().success(Boolean(node.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_NullNode(self, node, context, bin_op_right=False):
        return RTResult().success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context, bin_op_right=False):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context, bin_op_right)))
            if res.should_return(): return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ObjectNode(self, node, context, bin_op_right=False):
        res = RTResult()
        elements = {}

        for element in node.element_nodes:
            elements[element[0].value] = res.register(self.visit(element[1], context, bin_op_right))
            if res.should_return(): return res

        return res.success(
            Object(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context, bin_op_right=False):
        res = RTResult()
        var_name = node.var_name_tok.value
        if not bin_op_right:
            value = context.symbol_table.get(var_name)
            if isinstance(value, tuple):
                value, public = value
            if not value:
                return res.failure(
                    RTError(
                        node.pos_start, node.pos_end,
                        f"'{var_name}' is not defined",
                        context
                    )
                )

            value = value.copy().set_pos(context).set_context(context)
            return res.success(value)
        return res.success(var_name)

    def visit_VarAssignNode(self, node, context, bin_op_right=False):
        res = RTResult()
        var_name = node.var_name_tok.value
        update = node.update
        assign_type = node.assign_type
        isPublic = node.public
        value = res.register(self.visit(node.value_node, context, bin_op_right))
        if res.should_return(): return res

        if update:
            u_value = context.symbol_table.get(var_name)
            if isinstance(u_value, tuple):
                u_value, public = u_value
            if not u_value:
                return res.failure(
                    RTError(
                        node.pos_start, node.pos_end,
                        f"'{var_name}' is not defined",
                        context
                    )
                )
            
            if assign_type == TT_PE:
                result, error = u_value.added_to(value)
                if error: return res.failure(error)
                value = result
            elif assign_type == TT_ME:
                result, error = u_value.subbed_by(value)
                if error: return res.failure(error)
                value = result

        context.symbol_table.set(var_name, (value, isPublic))
        return res.success(value)

    def visit_MultiVarAssignNode(self, node, context, bin_op_right=False):
        res = RTResult()
        var_names = node.var_name_toks
        assign_type = node.assign_type

        current_value = None
        i = 0
        for var_name in var_names:
            i += 1
            if current_value == None:
                value = context.symbol_table.get(var_name[0].value)
                if isinstance(value, tuple):
                    value, public = value

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
                if isinstance(value, tuple):
                    value, public = value

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
                    new_value = res.register(self.visit(node.value_node, context, bin_op_right))
                    isTuple = False
                    if var_names[len(var_names)-1][0].value in current_value.elements:
                        t_value = current_value.elements[var_names[len(var_names)-1][0].value]
                        if isinstance(t_value, tuple):
                            t_value, public = t_value
                            isTuple = True
                        
                        if assign_type == TT_PE:
                            result, error = t_value.added_to(new_value)
                            if error: return res.failure(error)
                            new_value = result
                        elif assign_type == TT_ME:
                            result, error = t_value.subbed_by(new_value)
                            if error: return res.failure(error)
                            new_value = result

                    if isTuple:
                        current_value.elements[var_names[len(var_names)-1][0].value] = (new_value, public)
                    else:
                        current_value.elements[var_names[len(var_names)-1][0].value] = new_value
                except:
                    return res.failure(
                        RTError(
                            var_name[1], var_name[2],
                            f"'{current_value}' is not a object",
                            context
                        )
                    )
        return res.success(context.symbol_table.get(var_names[0][0].value)[0])

    def visit_BinOpNode(self, node, context, bin_op_right=False):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context, bin_op_right))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context, node.op_tok.type == TT_DOT))
        if res.should_return(): return res

        if node.op_tok.type == TT_DOT:
            result, error = left.dotted_to(right, node.right_node.pos_start, node.right_node.pos_end)
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

    def visit_UnaryOpNode(self, node, context, bin_op_right=False):
        res = RTResult()
        number = res.register(self.visit(node.node, context, bin_op_right))
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
    
    def visit_IfNode(self, node, context, bin_op_right=False):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context, bin_op_right))
            if res.should_return(): return res
            
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context, bin_op_right))
                if res.should_return(): return res
                return res.success(Null().set_context(context).set_pos(node.pos_start, node.pos_end) if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context, bin_op_right))
            if res.should_return(): return res
            return res.success(Null().set_context(context).set_pos(node.pos_start, node.pos_end) if should_return_null else expr_value)

        return res.success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_SwitchNode(self, node, context, bin_op_right=False):
        res = RTResult()
        value = res.register(self.visit(node.value_node, context, bin_op_right))
        if res.should_return(): return res

        for case, expr in node.cases:
            case_value = res.register(self.visit(case, context, bin_op_right))
            if res.should_return(): return res

            if value.equals(case_value):
                res.register(self.visit(expr, context, bin_op_right))
                if res.should_return(): return res
                return res.success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))

        if node.default:
            res.register(self.visit(node.default, context, bin_op_right))
            if res.should_return(): return res
        
        return res.success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ForNode(self, node, context, bin_op_right=False):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context, bin_op_right))
        if res.should_return(): return res

        if not isinstance(start_value, Number):
                return res.failure(RTError(
                    start_value.pos_start, start_value.pos_end,
                    "Expected number",
                    context
                ))

        end_value = res.register(self.visit(node.end_value_node, context, bin_op_right))
        if res.should_return(): return res

        if not isinstance(end_value, Number):
                return res.failure(RTError(
                    end_value.pos_start, end_value.pos_end,
                    "Expected number",
                    context
                ))

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context, bin_op_right))
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

            value = res.register(self.visit(node.body_node, context, bin_op_right))
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

    def visit_ForObjectNode(self, node, context, bin_op_right=False):
        res = RTResult()
        elements = []

        _object = res.register(self.visit(node.object_tok, context, bin_op_right))
        if res.should_return(): return res

        if not isinstance(_object, Object):
                return res.failure(RTError(
                    _object.pos_start, _object.pos_end,
                    "Expected object",
                    context
                ))

        for k, v in _object.elements.items():
            context.symbol_table.set(node.var_name_key_tok.value, String(str(k)))
            context.symbol_table.set(node.var_name_value_tok.value, v)

            value = res.register(self.visit(node.body_node, context, bin_op_right))
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
    
    def visit_ForListNode(self, node, context, bin_op_right=False):
        res = RTResult()
        elements = []

        _list = res.register(self.visit(node.list_tok, context, bin_op_right))
        if res.should_return(): return res

        if not isinstance(_list, List):
                return res.failure(RTError(
                    _list.pos_start, _list.pos_end,
                    "Expected list",
                    context
                ))

        for i in _list.elements:
            context.symbol_table.set(node.var_name_tok.value, i)

            value = res.register(self.visit(node.body_node, context, bin_op_right))
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

    def visit_WhileNode(self, node, context, bin_op_right=False):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context, bin_op_right))
            if res.should_return(): return res

            if not condition.is_true(): break

            value = res.register(self.visit(node.body_node, context, bin_op_right))
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

    def visit_FuncDefNode(self, node, context, bin_op_right=False):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        isPublic = node.public
        func_value = Function(func_name, body_node, node.arg_name_toks, node.should_auto_return, isPublic, context).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, (func_value))

        return res.success(func_value)
    
    def visit_CallNode(self, node, context, bin_op_right=False):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context, bin_op_right))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, value_to_call.lib if isinstance(value_to_call, Function) else context, bin_op_right)))
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)

    def visit_ImportNode(self, node, context, bin_op_right=False):
        res = RTResult()

        lib_name = res.register(self.visit(node.lib_name, context, bin_op_right))
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

        from BananaPlus import workspace_dir, lib_dir, file_id
        if lib_name.endswith(file_id):
            path = workspace_dir + "\\" + lib_name
        else:
            path = lib_dir + "\\" + lib_name + file_id

        try:
            with open(path, "r") as f:
                script = f.read()
                f.close()
        except Exception as e:
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                F"Failed to load script \"{path}\"\n" + str(e),
                context
            ))
        
        from BananaPlus import import_lib

        symbol_table, result, error = import_lib(lib_name, script, context)

        if error:
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                f"Failed to finish executing script \"{path}\"\n" + error.as_string(),
                context
            ))

        items_to_push = {}

        for key, value in symbol_table.symbols.items():
            if isinstance(value, Function):
                if value.isPublic:
                    items_to_push[key] = value
            elif isinstance(value, tuple):
                if value[1] == True:
                    items_to_push[key] = value

        context.symbol_table.set(var_name, Object(items_to_push))

        return RTResult().success(Null().set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_ReturnNode(self, node, context, bin_op_right=False):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context, bin_op_right))
            if res.should_return(): return res
        else:
            value = Null()

        return res.success_return(value)

    def visit_ContinueNode(self, node, context, bin_op_right=False):
        return RTResult().success_continue()
    
    def visit_BreakNode(self, node, context, bin_op_right=False):
        return RTResult().success_break()