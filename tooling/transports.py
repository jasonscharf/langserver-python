import SocketServer
import json
import sys
import traceback

from utils import echo
from jsonrpc import dispatcher
from rpc import process


class StdioTransport:
	"""Simple transport with minimal protocol overhead (i.e. no HTTP). Depends on unbuffered IO."""

	def handle(self, input, output):
		header_content_len = input.readline().strip()

		echo("RECV Header {}".format(header_content_len))
		content_len = int(header_content_len.split(": ")[1])

		header_content_type_or_newline = input.readline().strip()

		# TODO: Remove if supporting HTTP+JSON-RPC not needed
		if len(header_content_type_or_newline) < 1:
			echo("Received last header")

		body = input.read(content_len)
		echo("Read {} bytes of request body:\n{}".format(content_len, body))

		response_envelope = process(body)
		if response_envelope is None:
			return

		response_body = json.dumps(response_envelope)
		response_len = len(response_body)

		echo("RESP {}".format(json.dumps(response_body)))

		output.write("{}!".format(response_len)) # TODO
		output.write(response_body)

		return


class SocketTransport(SocketServer.StreamRequestHandler):
	"""Simple TCP/IP socket transport."""
	def handle(self):
		while True:
			try:
				input = self.rfile
				output = self.wfile

				# TODO: Handle other headers
				header_content_len = input.readline().strip()
				content_len = int(header_content_len.split(": ")[1])

				header_content_type_or_newline = input.readline().strip()

				# TODO: Remove if supporting HTTP JSON-RPC not needed
				if len(header_content_type_or_newline) < 1:
					echo("Received last header")

				body = input.read(content_len)
				echo("Read {} bytes of request body:\n{}".format(content_len, body))

			except KeyboardInterrupt:
				server.shutdown()
				sys.exit()

			try:
				response_envelope = process(body)

				if response_envelope is not None:
					response_body = json.dumps(response_envelope)
					response_len = len(response_body)

					resp = "Content-Length: {}\r\n\r\n{}".format(response_len, response_body)
					echo("RESP {}".format(resp))

			except:
				traceback.print_exc(file=sys.stdout)
				echo("Unexpected error: {}".format(sys.exc_info()[0]))

			output.write(resp)

		return
