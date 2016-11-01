from utils import sanitize


# Processes arguments to LSP requests that contain `TextDocumentIdentifier` and `Position` members (get refs, defs, etc.)
class DocRef:
	def __init__(self, params):
		raw_uri = params["textDocument"]["uri"]

		self.uri = sanitize(raw_uri);
		self.position = params["position"]
		self.line = int(self.position["line"]) + 1
		self.character = int(self.position["character"]) + 1
