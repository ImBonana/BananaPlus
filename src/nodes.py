class NumberNode:
	def __init__(self, tok, pos_start, pos_end):
		self.tok = tok

		self.pos_start = pos_start
		self.pos_end = pos_end

class StringNode:
	def __init__(self, tok, pos_start, pos_end):
		self.tok = tok

		self.pos_start = pos_start
		self.pos_end = pos_end

class ListNode:
	def __init__(self, element_nodes, pos_start, pos_end):
		self.element_nodes = element_nodes

		self.pos_start = pos_start
		self.pos_end = pos_end

class ObjectNode:
	def __init__(self, element_nodes, pos_start, pos_end):
		self.element_nodes = element_nodes

		self.pos_start = pos_start
		self.pos_end = pos_end

class BooleanNode:
	def __init__(self, value, pos_start, pos_end):
		self.value = value

		self.pos_start = pos_start
		self.pos_end = pos_end

class NullNode:
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end

class VarAccessNode:
	def __init__(self, var_name_tok, pos_start, pos_end):
		self.var_name_tok = var_name_tok

		self.pos_start = pos_start
		self.pos_end = pos_end

class VarAssignNode:
	def __init__(self, var_name_tok, value_node, assign_type, public, update=False, pos_start=None, pos_end=None):
		self.var_name_tok = var_name_tok
		self.value_node = value_node
		self.assign_type = assign_type
		self.public = public
		self.update = update

		self.pos_start = pos_start
		self.pos_end = pos_end

class MultiVarAssignNode:
	def __init__(self, var_name_toks, value_node, assign_type, pos_start, pos_end):
		self.var_name_toks = var_name_toks
		self.value_node = value_node
		self.assign_type = assign_type

		self.pos_start = pos_start
		self.pos_end = pos_end

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node, pos_start, pos_end):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = pos_start
		self.pos_end = pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node, pos_start, pos_end):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

class IfNode:
	def __init__(self, cases, else_case, pos_start, pos_end):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = pos_start
		self.pos_end = pos_end

class SwitchNode:
	def __init__(self, value_node, cases, default, pos_start, pos_end):
		self.value_node = value_node
		self.cases = cases
		self.default = default

		self.pos_start = pos_start
		self.pos_end = pos_end

class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null, pos_start, pos_end):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.pos_start = pos_start
		self.pos_end = pos_end

class ForObjectNode:
	def __init__(self, var_name_key_tok, var_name_value_tok, object_tok, body_node, should_return_null, pos_start, pos_end):
		self.var_name_key_tok = var_name_key_tok
		self.var_name_value_tok = var_name_value_tok
		self.object_tok = object_tok
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.pos_start = pos_start
		self.pos_end = pos_end

class ForListNode:
	def __init__(self, var_name_tok, list_tok, body_node, should_return_null, pos_start, pos_end):
		self.var_name_tok = var_name_tok
		self.list_tok = list_tok
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.pos_start = pos_start
		self.pos_end = pos_end

class WhileNode:
	def __init__(self, condition_node, body_node, should_return_null, pos_start, pos_end):
		self.condition_node = condition_node
		self.body_node = body_node
		self.should_return_null = should_return_null

		self.pos_start = pos_start
		self.pos_end = pos_end

class FuncDefNode:
	def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return, public, pos_start, pos_end):
		self.var_name_tok = var_name_tok
		self.arg_name_toks = arg_name_toks
		self.body_node = body_node
		self.should_auto_return = should_auto_return
		self.public = public

		self.pos_start = pos_start
		self.pos_end = pos_end

class CallNode:
	def __init__(self, node_to_call, arg_nodes, pos_start, pos_end):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = pos_start
		self.pos_end = pos_end

class ReturnNode:
	def __init__(self, node_to_return, pos_start, pos_end):
		self.node_to_return = node_to_return

		self.pos_start = pos_start
		self.pos_end = pos_end

class ContinueNode:
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end

class BreakNode:
	def __init__(self, pos_start, pos_end):
		self.pos_start = pos_start
		self.pos_end = pos_end

class ImportNode:
	def __init__(self, lib_name, var_name, pos_start, pos_end):
		self.lib_name = lib_name
		self.var_name = var_name

		self.pos_start = pos_start
		self.pos_end = pos_end