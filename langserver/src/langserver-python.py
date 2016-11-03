#!/usr/bin/env python2.7

import SocketServer 
import threading
import argparse
import jedi
import json
import sys
import os

import transports
import constants

from utils import echo
from handlers import preinit, initialize, didOpen, hover, definition, references


def serve(args):
	if args.socks is False:
		mode = "stdio"
	else:
		mode = "sockets"


	if mode == "stdio":
		server = transports.JsonRPCTransport()
		echo("Python language server. Mode: stdio")

		while True:
			ret = server.handle(sys.stdin, sys.stdout)
			if ret == -1:
				echo("Stopping.")

				break

	elif mode == "sockets":
		echo("Python language server. Mode: TCP/IP on {}:{}".format(args.host, args.port))
		host = args.host
		port = int(args.port)

		try:
			server = SocketServer.TCPServer((host, port), transports.SocketTransport)
			server.serve_forever()
		
		except SystemExit:
			server.shutdown()

		except KeyboardInterrupt:
			server.shutdown()
			sys.exit()

	else:
		echo("Invalid mode '{}'".format(mode))


def main():
	parser = argparse.ArgumentParser(description="Python Jedi")
	parser.add_argument("--socks", action='store_true', help='Runs the server over tcp', default=False)
	parser.add_argument("--host", help='The port to host the language server on', nargs='?', default=constants.default_host)
	parser.add_argument("--port", help='The hostname to listen on', nargs='?', default=constants.default_port)

	args = parser.parse_args()
	serve(args)


if __name__ == "__main__":
	main()
