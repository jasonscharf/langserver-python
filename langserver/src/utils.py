import os
import re
import sys
import urllib.parse, urllib.error

import constants


def get_symbol_kind(definition):
	if definition.type is None:
		return None

	if definition.type in constants.kinds:
		return constants.kinds[definition.type]

	return None


def make_symbol_info():
	symbol = {}
	return symbol


def make_error(code, message):
	error = {}
	error["code"] = code
	error["message"] = message
	return error


def echo(str):
	sys.stderr.write(str + '\n')
	return


def sanitize(uri):
	uri = uri.strip()

	if uri.startswith('file:///'):
		uri = uri[7:]

	uri = urllib.parse.unquote(uri)
	uri = uri.replace("\\", '/')

	# Strip leading slash from absolute NTFS-style paths containing a drive letter, i.e. '/c:/projects/' => 'c:/projects/''
	if uri.startswith('/') and re.match('^\/\w:', uri) is not None:
		uri = uri[1:]

	return uri

def normalize_vsc_uri(path):
	uri = path.replace('\\', '/')
	uri = urllib.parse.quote(uri)

	if uri.startswith('/'):
		uri = 'file://%s' % uri
	else:
		uri = 'file:///%s' % uri

	return uri
