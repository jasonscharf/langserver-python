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
	request_method = request_envelope.get("method", "ping")
	request_id = request_envelope.get("id", -1)
	request_params = request_envelope.get("params", {})

	echo("Request {} with method '{}', length {} bytes".format(request_id, request_method, content_len))

	# Map to LSP names
	if request_method == "textDocument/didOpen":
		request_method = "didOpen"

	handler = dispatcher.get("{}".format(request_method))
	payload = {}

	if handler is None:
		echo("Request {} has unknown method '{}'".format(request_id, request_method))
		payload = make_error(-32601, "Unknown method {}".format(request_method))

	else:
		payload = handler(request_id, request_method, request_params)


	# Request ID of -1 indicates notification and therefore has no response
	if request_id == -1:
		return


	response_envelope = {}
	response_envelope["jsonrpc"] = "2.0"
	response_envelope["id"] = request_id
	response_envelope["result"] = payload # TODO: Not if error

	return response_envelope
