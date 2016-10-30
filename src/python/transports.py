import SocketServer
import json
import sys
import os
import traceback

from utils import echo
from jsonrpc import dispatcher
from rpc import process


# TODO: Reconcile these two
# Note: Other headers (i.e. the vscode mime-type bearer) not currently supported (but simple enough to implement)
class StdioTransport:
	"""Simple transport with minimal protocol overhead (i.e. no HTTP). Depends on unbuffered IO."""

	def handle(self, input, output):
		header_content_len = input.readline().strip()
		content_len = int(header_content_len.split(": ")[1])
		header_content_type_or_newline = input.readline().strip()

		# TODO: Remove if supporting HTTP+JSON-RPC not needed
		if len(header_content_type_or_newline) < 1:
			echo("Received last header")

		body = input.read(content_len)
		response_envelope = process(body)

		if response_envelope is None:
			return

		response_body = json.dumps(response_envelope)
		response_len = len(response_body)

		echo("Respond {}".format(json.dumps(response_body)))

		# Note: Currently using off-brand JSON-RPC for detailed debugging purposes (silent proto failures in VSC)
		#resp = "Content-Length: {}\r\n\r\n{}".format(response_len, response_body)
		output.write("{}!".format(response_len))
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
				#if len(header_content_type_or_newline) < 1:
				#	echo("Received last header")

				body = input.read(content_len)
				echo("Read {} bytes of request body:\n{}".format(content_len, body))

			except KeyboardInterrupt:
				self.finish()
				sys.exit()
				return

			try:
				response_envelope = process(body)

				if response_envelope == 0:
					resp = response_envelope
					self.finish()
					sys.exit(response_envelope)
					return

				elif response_envelope is not None:
					response_body = json.dumps(response_envelope)
					response_len = len(response_body)

					resp = "Content-Length: {}\r\n\r\n{}".format(response_len, response_body)
					echo("Respond {}".format(resp))

			except:
				traceback.print_exc(file=sys.stdout)
				echo("Unexpected error: {}".format(sys.exc_info()[0]))
				# TODO: Error RESP for fatals

			output.write(resp)

		return
