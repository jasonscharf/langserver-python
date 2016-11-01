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
					# TODO: Handle MIME-type header from VS Code
					header_content_len = input.readline().strip()
					content_len = int(header_content_len.split(": ")[1])

					header_content_type_or_newline = input.readline().strip()

				except:
					traceback.print_exc(file=sys.stderr)
					echo("Error reading message header: {}".format(sys.exc_info()[0]))
					echo("Received: {}".format(header_content_len))
					return

				# TODO: Remove if supporting HTTP JSON-RPC not needed
				#if len(header_content_type_or_newline) < 1:
				#	echo("Received last header")

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
					resp = "Content-Length: {}\r\n\r\n{}".format(response_len, response_body)

				echo("Respond {}".format(resp))
				output.write(resp)

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
