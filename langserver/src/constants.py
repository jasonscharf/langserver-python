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
kinds = {
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
