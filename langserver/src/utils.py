import os
import re
import sys
import urllib.parse, urllib.error

import constants


def extract_textdocument_pos(definition):
	uri = ''
	if definition.module_path is not None:
		uri = normalize_vsc_uri(definition.module_path)
	elif definition.name is not None:
		uri = normalize_vsc_uri(definition.name)

	line = definition.line;
	column = definition.column;

	# Builtins lack line/col and resolvable 'module_path'
	if line is None:
		return None

	# One position is used for the start and end of the range because VSC - at the least - works it out to mean the entire line
	# Not sure if this is noted and/or buried in protocol.md somewhere, but I've seen it mentioned.
	pos = {
		"line": line - 1,
		"character": column
	}
	item = {
		"uri": uri,
		"range": {
			"start": pos,
			"end": pos
		}
	}

	return item


def get_symbol_kind(definition):
	if definition.type is None:
		return None

	if definition.type in constants.jedi_kinds:
		return constants.jedi_kinds[definition.type]

	return None


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
