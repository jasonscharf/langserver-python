import os
import jedi
import json
import sys
import traceback
import constants

from workspace import Workspace
from docref import DocRef
from utils import echo, sanitize, normalize_vsc_uri, make_error, get_symbol_kind


# Global workspace instance
workspace = Workspace()

def preinit(args):
	echo("Pre-initializing the Jedi server...")
	# TODO (jscharf): Preload costly packages, e.g. numpy.


#
# LSP initialize
#
def initialize(id, method, params):
	rootPath = sanitize(params.get('rootPath', '.'))
	workspace.root = rootPath

	echo("Initialize received. Workspace root: %s" % (rootPath))

	capabilities = {}
	capabilities["textDocumentSync"] = 1 # none=0, full=1, incremental=2
	capabilities["hoverProvider"] = True
	capabilities["definitionProvider"] = True
	capabilities["referencesProvider"] = True
	capabilities["workspaceSymbolProvider"] = True

	resp = {}
	resp["capabilities"] = capabilities
	return resp


#
# LSP textDocument/didOpen
#
def didOpen(id, method, params):
	uri = params["textDocument"]["uri"]
	content = params["textDocument"]["text"]
	doc = workspace.open_with_content(uri, content, False)
	return


#
# LSP textDocument/didChange
#
def didChange(id, method, params):
	uri = params["textDocument"]["uri"]
	changes = params["contentChanges"]

	# Note: Incremental not supported! Also, this is specifically for IDE support and not for backend at this point.
	text = changes[0]["text"]
	doc = workspace.update(uri, text, False)
	return


#
# LSP textDocument/hover
#
def hover(id, method, params):
	items = []

	try:
		docref = DocRef(params)
		uri = sanitize(docref.uri)
		doc = workspace.open(uri, True)
		content = doc.content

		definitions = []
		script = jedi.api.Script(source=content, line=docref.line, column=docref.character, path=docref.uri)
		definitions = script.goto_definitions()

		for definition in definitions:
			item = {
				'value': definition.name
			}
			items.append(item)
			break

	# Jedi throws on columns at the end of lines
	except ValueError:
		exception_msg = traceback.format_exc()
		if 'valid range' in exception_msg:
			pass
		else:
			echo(exception_msg)
			msg = "Error (textDocument/hover): {}".format(sys.exc_info()[0])
			return make_error(constants.error, msg)

	resp = {
		"contents": items
	}
	return resp


#
# LSP textDocument/definition
#
def definition(id, method, params):
	items = []
	try:
		docref = DocRef(params)
		content = workspace.open(docref.uri, False).content
		script = jedi.api.Script(source=content, line=docref.line, column=docref.character, path=docref.uri)

		# See note re: differences between goto_assignments and goto_definitions here (from http://jedi.jedidjah.ch/en/latest/docs/plugin-api.html#jedi.api.Script.goto_definitions):
		definitions = script.goto_definitions()
		for definition in definitions:

			# If true, it's a def and not a ref
			if not definition.is_definition():
				continue

			# TODO (jscharf): Extract
			uri = ''
			if definition.module_path is not None:
				uri = normalize_vsc_uri(definition.module_path)
			elif definition.name is not None:
				uri = normalize_vsc_uri(definition.name)

			# One position is used for the start and end of the range because VSC - at the least - works it out to mean the entire line
			# Not sure if this is noted and/or buried in protocol.md somewhere, but I've seen it mentioned.
			pos = {
				"line": definition.line - 1,
				"character": definition.column
			}
			item = {
				"uri": uri,
				"range": {
					"start": pos,
					"end": pos
				}
			}

			items.append(item)

	except:
		echo(traceback.format_exc())
		msg = "Error (textDocument/definition): {}".format(sys.exc_info()[0])
		return make_error(constants.error, msg)

	return items


#
# LSP textDocument/references
#
def references(id, method, params):
	refs = []
	try:
		docref = DocRef(params)
		context = params["context"]
		include_decl = context.get("includeDeclaration", False)

		content = workspace.open(docref.uri, False).content
		script = jedi.api.Script(source=content, line=docref.line, column=docref.character, path=docref.uri)
		usages = script.usages()
		for usage in usages:
			if usage.is_definition() and include_decl is not True:
				continue
			if usage.line is None:
				continue

			uri = ''
			if usage.module_path is not None:
				uri = normalize_vsc_uri(usage.module_path)
			elif usage.name is not None:
				uri = normalize_vsc_uri(usage.name)

			pos = {
				"line": usage.line - 1,
				"character": usage.column
			}
			item = {
				"uri": uri,
				"range": {
					"start": pos,
					"end": pos
				}
			}

			refs.append(item)

	except:
		echo(traceback.format_exc())
		msg = "Error (textDocument/references): {}".format(sys.exc_info()[0])
		return make_error(constants.error, msg)

	return refs


#
# LSP workspace/symbol
#
def symbol(id, method, params):
	symbols = {}
	try:
		query_external_refs_only = False
		query_exported_defs_only = False
		query_empty = False

		raw_query = params['query'].strip()

		# Default to 10 but respect the desired limit if it's under an absolute max
		query_limit = constants.query_limit_default
		if 'limit' in params:
			query_limit = min(params['limit'], constants.query_limit_absolute)

		# See https://github.com/sourcegraph/langserver#lsp-method-details
		if raw_query.startswith(constants.query_is_ext_ref):
			query = raw_query[len(constants.query_is_ext_ref) + 1:]
			query_external_refs_only = True

		elif raw_query.startswith(constants.query_is_exported):
			query = raw_query[len(constants.query_is_exported) + 1:]
			query_exported_defs_only = True

		elif raw_query == "":
			query = ""
			query_empty = True

		else:
			query = raw_query
		
		# Note: Query string is case insensitive, as are the symbol names it is tested against
		query = query.strip().lower()
		query_len = len(query)

		candidate_files = [] 

		# Search workspace for all files ending in .py
		try:

			# TODO: Extract to workspace, virtualize entirely
			for root, subs, files in os.walk(workspace.root):
				for filename in files:
					if filename.endswith(".py") is False:
						continue

					#echo('Search candidate %s' % filename)
					filename = os.path.join(root, filename);
					filename = sanitize(filename)
					candidate_files.append(filename)

		except IOError:
			echo(traceback.format_exc())
			msg = "Error (workspace/symbol): {}".format(sys.exc_info()[0])
			return make_error(constants.error, msg)

		for file in candidate_files:

			# Perf: Caching these per file + dirty-tracking may yield tangible performance benefits
			file_symbols = jedi.api.names(path=file, encoding='utf-8', definitions=True, references=False, all_scopes=True)

			seen_symbols = {}
			for symbol in file_symbols:

				# Memoize symbols we've seen
				if symbol.full_name in seen_symbols:
					continue
				else:
					seen_symbols[symbol.full_name] = symbol


				# No module_path? Outside of workspace, builtin?
				if symbol.module_path is None:
					continue

				# Filter based on the query string
				name = symbol.name.lower()
				symbol_name = symbol.name.lower()
				name = symbol.name.lower()
				full_name = symbol.full_name.lower()
				module_name = symbol.module_name.lower()
				parent = symbol.parent()
				parent_name = None

				if parent is not None:
					parent_name = parent.name

				# Check symbol name and full name. Checking full name catches symbols with non-matching names that are imported from modules with matching names.
				# For example, querying for "util" should yield "utils.echo", even though "echo" has a non-matching symbol name "echo" and it may not be ref'd via its FQ name.
				if query_empty is False:
					if query in symbol_name:
						symbol_name = symbol.name
					
					elif symbol.type == 'module':
						symbol_name = module_name

					else:
						continue
				else:
					# Empty queries "match" against full names. This is clearer from a UX perspective.
					symbol_name = symbol.full_name

				key = '%s-%s-%s' % (symbol.module_path, symbol.name, symbol.type or '[any]')
				if key in symbols:
					continue

				uri = normalize_vsc_uri(symbol.module_path)
				pos = {
					"line": symbol.line - 1,
					"character": symbol.column
				}
				location = {
					'uri': uri,
					'range': {
						'start': pos,
						'end': pos
					}
				}
				item = {
					'name': symbol_name,
					'kind': get_symbol_kind(symbol),
					'location': location,
					'containerName': parent_name
				}
				symbols[key] = item

				# Enforce query limits
				if len(symbols) >= query_limit:
					break

	except:
		echo(traceback.format_exc())
		msg = "Error (workspace/symbol): {}".format(sys.exc_info()[0])
		return make_error(constants.error, msg)

	return list(symbols.values()) or []


#
# LSP exit
#
def exit(id, method, params):
	# -1 is used as a simple exit signal and relayed back to the transport to shut down cleanly
	return -1


#
# LSP shutdown
#
def shutdown(id, method, params):
	return {}
