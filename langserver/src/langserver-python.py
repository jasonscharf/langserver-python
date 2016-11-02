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
	if args.stdio:
		mode = "stdio"
	else:
		mode = "sockets"

	if mode == "stdio":
		server = transports.JsonRPCTransport()
		echo("Python language server. Mode: stdio")

		while True:
			server.handle(sys.stdin, sys.stdout)

	elif mode == "sockets":
		echo("Python language server. Mode: TCP/IP on {}:{}".format(args.host, args.port))
		host = args.host
		port = int(args.port)

		try:
			server = SocketServer.TCPServer((host, port), transports.SocketTransport)
			server.serve_forever()
			
		except KeyboardInterrupt:
			server.shutdown()
			sys.exit()

	else:
		echo("Invalid mode '{}'".format(mode))


def query(args):
	if args.path == "":
		echo("ls-python: path is empty")
		sys.exit(2)

	elif args.line < 1:
		echo("ls-python: line is not valid")
		sys.exit(2)

	elif args.column < 0:
		echo("ls-python: column is not valid")
		sys.exit(2)

	if args.subcmd == "hover":
		hover(args)

	elif args.subcmd == "definition":
		definition(args)

	elif args.subcmd == "references":
		references(args)

	else:
		echo("Sorry, I don't understand..")


def addSourceArgs(parser):
	# TODO: Look into a cleaner way of doings this, i.e. groups or something
	parser.add_argument('line', help='The line to perform actions on (starting with 1).', nargs='?', default=1, type=int)
	parser.add_argument('column', help='The column of the cursor (starting with 0).', nargs='?', default=0, type=int)
	parser.add_argument('path', help='The path of the file in the file system.', nargs='?', default=constants.default_path)


def main():
	parser = argparse.ArgumentParser(description="Python Jedi")
	parser.add_argument("--pre", help='', default=None)
	parser.add_argument("--stdio", action='store_true', help='Runs the server over stdio', default=False)
	parser.add_argument("--host", help='The port to host the language server on', nargs='?', default=constants.default_host)
	parser.add_argument("--port", help='The hostname to listen on', nargs='?', default=constants.default_port)
	parser.set_defaults(func=serve)

	args = parser.parse_args()

	#if args.pre is not None:
	#	preinit(args)

	args.func(args)


if __name__ == "__main__":
	main()
