from utils import echo
from document import Document

class Workspace:
	"""Represents a virtual 'workspace' that provides simple lifecycle management over a set of Documents."""
	root = "."
	documents = {}

	def open_with_content(self, path, content):
		doc = self.get(path)
		if doc is None:
			echo("Adding script '{}'".format(path))
			doc = Document()
			doc.uri = path
			doc.content = content
			self.documents[path] = doc

		return doc

	def open_from_fs(self, path):
		rooted_path = os.path.join(self.root, path)
		doc = self.get(path)
		source = workspace.open(rooted_path).read()

		self.documents[path] = doc
		return source

	def get(self, path):
		existing = self.documents.get(path)

		if existing is not None:
			echo("Found existing doc '{}'".format(path))
			return existing

		return None

	def update(self, path, content):
		# TODO
		return
