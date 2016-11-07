import socketserver
import json
import sys
import os
import traceback
import select

import constants
from utils import echo
from rpc import process


# Note: Other headers (i.e. the vscode mime-type bearer) not currently supported (but simple enough to implement)
class JsonRPCTransport:
	"""Simple transport with minimal protocol overhead (i.e. no HTTP). Depends on TCP/IP or unbuffered stdio."""

	def handle(self, input, output):
		try:
			has_content_length = False

			while True:
				echo("Read...")
				header = sys.stdin.readline()
				if len(header) == 0:
					echo("Receive EOF")
					return -1

				header = header.strip()
				# We care about "Content-Length", newlines, and JSON-RPC bodies, that's it at this point
				if header.startswith("Content-Length:") is True:
					content_len = int(header.split(": ")[1])
					has_content_length = True
					continue

				elif len(header) > 0:
					echo("Disregard header '{}'...continue".format(header))
					continue

				elif len(header) == 0 and has_content_length is True:
					break

				else:
					continue
		
		except KeyboardInterrupt:
			return -1

		except:
			echo(traceback.format_exc())
			echo("Error reading message header: {}".format(sys.exc_info()[0]))
			return -1


		try:
			body = input.read(content_len)
			response_envelope = process(body)

			if response_envelope == -1:
				echo("Received 'exit'...exiting")
				resp = response_envelope
				return -1

			elif response_envelope is not None:
				response_body = json.dumps(response_envelope)
				response_len = len(response_body)


				resp = "Content-Length: {}\r\n{}\r\n\r\n{}".format(response_len, constants.lsp_content_type, response_body)

			else:
				resp = None

			# Respond when we have responses but not for notifications.
			# In the interests of simplicity, handlers can just return `None` if they are acting on notifications.
			if resp is not None:
				echo("============================================================")
				echo("Respond {}".format(resp))
				echo("============================================================")

				output.write(resp)
				output.flush()

				echo("flushed")

		except KeyboardInterrupt:
			return -1

		except:
			echo(traceback.format_exc())
			echo("Transport error: {}".format(sys.exc_info()[0]))
			return -1


class SocketTransport(socketserver.StreamRequestHandler):
	"""Simple TCP/IP socket transport."""
	jsonrpc = JsonRPCTransport()

	def handle(self):
		input = self.rfile
		output = self.wfile
		ret = self.jsonrpc.handle(input, output)

		if ret == -1:
			self.end()
			self.finish()
