import json

from jsonrpc import dispatcher
from utils import echo


def make_error(code, message):
	error = {}
	error["code"] = code
	error["message"] = message
	return error


def process(body):
	content_len = len(body)
	request_envelope = json.loads(body)
	method = request_envelope.get("method", "ping")
	request_id = request_envelope.get("id", -1)
	request_params = request_envelope.get("params", {})

	# Map to LSP names, but safely
	request_method_safe = "noop"
	if method == "initialize":
		request_method_safe = "initialize"
	elif method == "textDocument/didOpen":
		request_method_safe = "didOpen"
	elif method == "textDocument/hover":
		request_method_safe = "hover"
	elif method == "textDocument/definition":
		request_method_safe = "definition"
	elif method == "textDocument/references":
		request_method_safe = "references"
	elif method == "textDocument/didChange":
		request_method_safe = "didChange"
	elif method == "workspace/symbol":
		request_method_safe = "symbol"
	elif method == "shutdown":
		request_method_safe = "shutdown"
	elif method == "exit":
		request_method_safe = "exit"

	handler = dispatcher.get("{}".format(request_method_safe))
	payload = {}

	if handler is None:
		echo("Request {} has unknown method '{}'".format(request_id, method))
		payload = make_error(-32601, "Unknown method {}".format(method))

	else:
		payload = handler(request_id, method, request_params)


	# Request ID of -1 indicates notification and therefore has no response
	if request_id == -1:
		return


	response_envelope = {}
	response_envelope["jsonrpc"] = "2.0"
	response_envelope["id"] = request_id
	response_envelope["result"] = payload # TODO: Not if error

	return response_envelope
