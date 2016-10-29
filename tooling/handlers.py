from jsonrpc import dispatcher
from globals import workspace
from utils import echo


def preinit(args):
	echo("Pre-initializing the Jedi server...")
	# TODO: Preload costly packages, e.g. numpy.


# Note: Initialize logic is currently handled by JediHarness.
@dispatcher.add_method
def initialize(id, method, params):
	echo("Initialize received. Workspace root: {}".format(params["rootPath"]))


	capabilities = {}
	capabilities["textDocumentSync"] = 1 # none=0, full=1, incremental=2
	capabilities["hoverProvider"] = True
	capabilities["definitionProvider"] = True
	capabilities["referencesProvider"] = True

	# TODO: Remove. Slightly useful for debugging/perf purposes but not currently supported.
	completion_provider_cap = {}
	completion_provider_cap["resolveProvider"] = True
	capabilities["completionProvider"] = completion_provider_cap

	resp = {}
	resp["capabilities"] = capabilities
	return resp


@dispatcher.add_method
def didOpen(id, method, params):
	uri = params["textDocument"]["uri"]
	content = params["textDocument"]["text"]
	doc = workspace.open_with_content(uri, content)
	return


@dispatcher.add_method
def hover(args):
	source = workspace.open(args.uri).read()
	script = jedi.api.Script(source=source, line=args.line, column=args.column, path=args.path)

	for c in script.completions():
		docstring = c.docstring()
		if docstring == "":
			continue

		echo(c.docstring())
		sys.exit(0)
		break

	echo("No definition found")
	return


@dispatcher.add_method
def definition(args):
	source = open(args.path, "r").read()
	script = jedi.api.Script(source=source, line=args.line, column=args.column, path=args.path)

	for a in script.goto_assignments():
		if not a.is_definition():
			continue

		json.dump({
			"path": a.module_path,
			"line": a.line,
			"column": a.column,
		}, sys.stdout, sort_keys=True)
		sys.exit(0)
		break

	echo("No definition found")
	return


@dispatcher.add_method
def references(args):
	source = open(args.path, "r").read()
	script = jedi.api.Script(source=source, line=args.line, column=args.column, path=args.path)

	usages = script.usages()
	if len(usages) == 0:
		echo("No references found")
		return

	results = []
	for u in usages:
		if u.is_definition():
			continue

		results.append({
			"path": u.module_path,
			"line": u.line,
			"column": u.column,
		})

	json.dump(results, sys.stdout, sort_keys=True)
	return


@dispatcher.add_method
def ping(id, method, params):
	echo("PING")
	resp = 1
	return resp
