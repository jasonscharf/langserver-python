default_path = __file__
default_mode = "query"
default_host = "localhost"
default_port = 9999

query_is_ext_ref = "is:external-reference"
query_is_exported = "is:exported"

# Limits for workspace/symbol
query_limit_default = 10
query_limit_absolute = 250

# LSP error codes
error = -32700
invalid_request = -32600
method_not_found = -32601
invalid_params = -32602
internal_error = -32603
server_error_start = -32099
server_error_start = -32000

# LSP trivia
lsp_content_type = "Content-Type: application/vscode-jsonrpc; charset=utf8"


# LSP kinds
vsc_kind = {
	'file': 1,
	'module': 2,
	'namespace': 3,
	'package': 4,
	'class': 5,
	'method': 6,
	'property': 7,
	'field': 8,
	'constructor': 9,
	'enum': 10,
	'interface': 11,
	'function': 12,
	'variable': 13,
	'constant': 14,
	'string': 15,
	'number': 16,
	'array': 18,
	'boolean': 17
}


# Jedi kinds from string
jedi_kinds = {

	# Note: Omissions due to unknown mappings:
	# 'statement': 0,
	# 'keyword': 0,

	# Jedi type 'none' maps to vsc variable
	'none': vsc_kind['constant'],
	'type': vsc_kind['class'],
	'tuple': vsc_kind['class'],

	# 'dict' => 'class'
	'dict': vsc_kind['class'],
	'dictionary': vsc_kind['class'],

	# Classes / instances
	'class': vsc_kind['class'],
	'instance': vsc_kind['variable'],

	# Functions
	'function': vsc_kind['function'],
	'lambda': vsc_kind['function'],
	'generator': vsc_kind['function'],
	'method': vsc_kind['method'],

	# Builtins
	'builtin': vsc_kind['class'],
	'builtinfunction': vsc_kind['function'],

	# Scopes
	'file': vsc_kind['file'],
	'namespace': vsc_kind['namespace'],
	'module': vsc_kind['module'],

	# Regular Python types
	'funcdef': vsc_kind['function'],
	'property': vsc_kind['property'],
	'import': vsc_kind['module'],

	# Primitives (Python-style)
	'constant': vsc_kind['constant'],
	'variable': vsc_kind['variable'],
	'value': vsc_kind['variable'],
	'param': vsc_kind['variable'],
	'boolean': vsc_kind['boolean'],
	'int': vsc_kind['number'],
	'longlean': vsc_kind['number'],
	'float': vsc_kind['number'],
	'complex': vsc_kind['number'],
	'string': vsc_kind['string'],
	'unicode': vsc_kind['string'],
	'list': vsc_kind['array'],

	# Special Python types
	'xrange': vsc_kind['class'],
	'slice': vsc_kind['class'],
	'traceback': vsc_kind['class'],
	'frame': vsc_kind['class'],
	'buffer': vsc_kind['class'],
	'dictproxy': vsc_kind['class'],
}
