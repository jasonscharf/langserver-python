import jedi
import sys
import constants

from workspace import Workspace
from docref import DocRef
from utils import echo, sanitize, normalize_vsc_uri

# Global workspace instance
workspace = Workspace()


def preinit(args):
	echo("Pre-initializing the Jedi server...")
	# TODO: Preload costly packages, e.g. numpy.


#
# LSP initialize
#
def initialize(id, method, params):
	echo("Initialize received. Workspace root: {}".format(params["rootPath"]))

	workspace.root = params["rootPath"]

	capabilities = {}
	capabilities["textDocumentSync"] = 1 # none=0, full=1, incremental=2
	capabilities["hoverProvider"] = True
	capabilities["definitionProvider"] = True
	capabilities["referencesProvider"] = True
	capabilities["workspaceSymbolProvider"] = True

	# TODO: Remove. Slightly useful for debugging/perf purposes but not currently supported.
	completion_provider_cap = {}
	completion_provider_cap["resolveProvider"] = True
	capabilities["completionProvider"] = completion_provider_cap

	# TODO: Consume other workspace documents - not just open documents!

	resp = {}
	resp["capabilities"] = capabilities
	return resp


#
# LSP textDocument/didOpen
#
def didOpen(id, method, params):
	uri = params["textDocument"]["uri"]
	content = params["textDocument"]["text"]
	doc = workspace.open_with_content(uri, content)
	return


#
# LSP textDocument/didChange
#
def didChange(id, method, params):
	uri = params["textDocument"]["uri"]
	changes = params["contentChanges"]

	# Note: Incremental not supported! Also, this is specifically for IDE support and not for backend at this point.
	text = changes[0]["text"]

	doc = workspace.update(uri, text)
	return


#
# LSP textDocument/hover
#
def hover(id, method, params):
	items = []
	try:
		docref = DocRef(params)
		content = workspace.open(docref.uri).content
		
		# Note: Jedi errors are supressed here due to sporadic failure on invalid column.
		completions = []
		try:
			script = jedi.api.Script(source=content, line=docref.line, column=docref.character, path=docref.uri)
			completions = script.completions()
		except:
			pass

		# Improvement: Jedi's API calls yield some overlapping results. Hover can be implemented in multiple ways
		for completion in completions:

			# Small markdown string that bolds the symbol's description
			item = "**%s**  \n%s" % (completion.description, completion.type)
			items.append(item)
			break

		# Return a sensible default. If don't find anything, look for defs and use the first definition we find
		if len(items) == 0:
			defs = script.goto_definitions()
			if len(defs) == 0:
				default_item = "(no info found)"
				items.append(default_item)
			else:
				first_def = defs[0]
				item = "**%s**  \n%s" % (first_def.description, first_def.type)

				items.append(item)

	except:
		raise

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
		content = workspace.open(docref.uri).content
		script = jedi.api.Script(source=content, line=docref.line, column=docref.character, path=docref.uri)

		# See note re: differences between goto_assignments and goto_definitions here (from http://jedi.jedidjah.ch/en/latest/docs/plugin-api.html#jedi.api.Script.goto_definitions):
		# Also... "Warning: Don't use this function yet, its behaviour may change. If you really need it, talk to me." :/
		definitions = script.goto_definitions()

		for definition in definitions:

			# If true, it's a def and not a ref
			if not definition.is_definition():
				continue

			path = normalize_vsc_uri(definition.module_path)
	
			# One position is used for the start and end of the range because VSC - at the least - works it out to mean the entire line
			# Not sure if this is noted and/or buried in protocol.md somewhere, but I've seen it mentioned.
			pos = {
				"line": definition.line - 1,
				"character": definition.column
			}
			item = {
				"uri": path,
				"range": {
					"start": pos,
					"end": pos
				}
			}

			items.append(item)

	except:
		raise

	return items


#
# LSP textDocument/references
#
def references(id, method, params):
	refs = []
	try:
		docref = DocRef(params)
		context = params["context"]
		include_decl = context["includeDeclaration"]
		content = workspace.open(docref.uri).content

		script = jedi.api.Script(source=content, line=docref.line, column=docref.character, path=docref.uri)
		usages = script.usages()

		for usage in usages:
			if usage.is_definition() and include_decl is not True:
				continue

			path = normalize_vsc_uri(usage.module_path)
			pos = {
				"line": usage.line - 1,
				"character": usage.column
			}
			item = {
				"uri": path,
				"range": {
					"start": pos,
					"end": pos
				}
			}

			refs.append(item)

	except:
		pass

	return refs


#
# LSP workspace/symbol
#
def symbol(id, method, params):
	candidates = {}
	try:
		query_external_refs_only = False
		query_exported_defs_only = False
		query_empty = False

		raw_query = params["query"].strip()

		# TODO (remove, for testing)
		raw_query = "%s %s" % (constants.query_is_ext_ref, raw_query)

		# See https://github.com/sourcegraph/langserver#lsp-method-details
		if raw_query.startswith(constants.query_is_ext_ref):
			query = raw_query[len(constants.query_is_ext_ref) + 1:]
			query_external_refs_only = True
		elif raw_query.startswith(constants.query_is_exported):
			query = raw_query[len(constants.query_is_exported) + 1:]
			query_exported_defs_only = True
		elif raw_query == "":
			query_empty = True
		else:
			query = raw_query

		query = query.strip()
		
		echo("Symbol query. Empty?: %s External? %s Exports only? %s Body: %s" % (query_empty, query_external_refs_only, query_exported_defs_only, query))

		query_len = len(query)

		# For each document in the workspace, get completions from the module scope of that document as if it were being typed in at the foot of the doc.
		# This is actually a pretty workable solution (initially). However, there are other options. This is a somewhat naive approach.
		for key, value in workspace:
			document = value
			line = document.lines + 1

			# Append the query string to the bottom of a synthesized "document" and at at the end of the query
			content = document.content + "\n" + query
			script = jedi.api.Script(source=content, line=line, column=query_len, path=key)

			# Improvement: goto_definitions use on the completions.
			for completion in script.completions():
				name = "%s (%s)" % (completion.name, completion.type)
				container = completion.full_name
				uri_raw = completion.module_path
				is_vendored = False

				# Note: Builtins have no 'module_path' (URI) and not considered vendor libs
				# See https://github.com/sourcegraph/langserver#lsp-method-details
				# TODO: Need to consider other packages tho
				if uri_raw is None:
					uri_raw = "[ext]/%s" % name

				if query_external_refs_only and is_vendored is True:
					continue

				if query_exported_defs_only and is_vendored is True:
					continue

				# In most languages, the only external refs available in a given scope will be ones exported from other (external) modules.
				# That's not the case with code search, which has looser rules than type systems and symbol trees.
				# That's why is_external and is_exported properties can be treated as distinct (although they're not here, currently).
				if is_vendored is True and sanitize(uri_raw) != document.uri:
					is_external = True
					is_exported = True
					echo("Found external ref '%s' for '%s'" % (sanitize(uri_raw), document.uri))

				uri = normalize_vsc_uri(uri_raw)
				line = completion.line

				# Builtins don't have positional info (at least not from completions)
				if line is None:
					echo("No line for completion '%s' @ %s" % (name, uri))
					line = 1
					column = 0

				pos = {
					"line": line - 1,
					"character": 0
				},

				item = {
					"name": name,
					"containerName": container,
					"kind": 1,
					"location": {
						"uri": uri,
						"range": {
							"start": pos,
							"end": pos
						}
					}
				}

				# Use of a dictionary prevents duplicates (from other in-scope refs in other documents)
				key = "%s::%s" % (completion.full_name, completion.type)
				candidates[key] = item

	# If this fails, it's for a reason worth raising - unlike certain Jedi exceptions re: line/char pos
	except:
		raise

	return candidates.values()


#
# LSP exit
#
def exit(id, method, params):
	# Note: It's up to transports to handle integer responses and exit accordingly
	return 0

#
# LSP shutdown
#
def shutdown(id, method, params):
	# Not for backend...
	return 0
