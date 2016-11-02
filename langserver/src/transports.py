import SocketServer
import json
import sys
import os
import traceback

from utils import echo
from rpc import process


# Note: Other headers (i.e. the vscode mime-type bearer) not currently supported (but simple enough to implement)
class JsonRPCTransport:
	"""Simple transport with minimal protocol overhead (i.e. no HTTP). Depends on TCP/IP or unbuffered stdio."""

	def handle(self, input, output):
		while True:
			try:
				try:
					has_content_length = False
					header_content_len = input.readline().strip()

					# We care about "Content-Length", newlines, and JSON-RPC bodies, that's it at this point
					if header_content_len.startswith("Content-Length:") is True:
						echo("Read content-len")
						content_len = int(header_content_len.split(": ")[1])
						has_content_length = True
						continue

					elif len(header_content_len) > 0:
						echo("Found HTTPish header '{}'...continue".format(header_content_len))
						continue


				except:
					traceback.print_exc(file=sys.stderr)
					echo("Error reading message header: {}".format(sys.exc_info()[0]))
					echo("Received: {}".format(header_content_len))
					return

				# TODO: Remove if supporting HTTP JSON-RPC not needed

				body = input.read(content_len)
				echo("Read {} bytes of request body:\n{}".format(content_len, body))

				response_envelope = process(body)

				if response_envelope == 0:
					resp = response_envelope
					sys.exit(response_envelope)
					return

				elif response_envelope is not None:
					response_body = json.dumps(response_envelope)
					response_len = len(response_body)
					content_type = "application/vscode-jsonrpc; charset=utf8"
					resp = "Content-Length: {}\r\n\r\n{}".format(response_len, response_body)

				echo("Respond {}".format(resp))
				output.write(resp)
				output.flush()

			except KeyboardInterrupt:
				sys.exit()
				return

			except:
				traceback.print_exc(file=sys.stderr)
				echo("Unexpected error: {}".format(sys.exc_info()[0]))
				# TODO: Error RESP for fatals


class SocketTransport(SocketServer.StreamRequestHandler):
	"""Simple TCP/IP socket transport."""
	jsonrpc = JsonRPCTransport()

	def handle(self):
		input = self.rfile
		output = self.wfile
		return self.jsonrpc.handle(input, output)
