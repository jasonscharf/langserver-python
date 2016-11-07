import json
import handlers
import constants

from utils import echo, make_error


def process(body):
	content_len = len(body)
	request_envelope = json.loads(body)
	method = request_envelope.get('method', 'ping')
	request_id = request_envelope.get('id', -1)
	request_params = request_envelope.get('params', {})

	# Map to LSP names
	handler = None
	if method == 'initialize':
		handler = handlers.initialize
	elif method == 'textDocument/didOpen':
		handler = handlers.didOpen
	elif method == 'textDocument/hover':
		handler = handlers.hover
	elif method == 'textDocument/definition':
		handler = handlers.definition
	elif method == 'textDocument/references':
		handler = handlers.references
	elif method == 'textDocument/didChange':
		handler = handlers.didChange
	elif method == 'workspace/symbol':
		handler = handlers.symbol
	elif method == 'shutdown':
		handler = handlers.shutdown
	elif method == 'exit':
		handler = handlers.exit

	payload = {}

	if handler is None:
		echo("Request {} has unknown method {}".format(request_id, method))
		payload = make_error(constants.method_not_found, "Unknown method {}".format(method))

	else:
		payload = handler(request_id, method, request_params)

	# Payload of -1 is a simple exit signal and is relayed to the transport
	if payload == -1:
		return -1

	# Request ID of -1 indicates notification and therefore has no response
	if request_id == -1:
		return None

	response_envelope = {}
	response_envelope['jsonrpc'] = '2.0'
	response_envelope['id'] = request_id

	# Relay errors
	if 'code' in payload:
		response_envelope['error'] = payload
		echo("Relay error")
	else:
		response_envelope['result'] = payload

	return response_envelope
