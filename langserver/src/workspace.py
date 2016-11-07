import os

from utils import echo, sanitize


class Document:
	uri = ""
	path = ""
	lines = ""
	content = ""


# Note: Not thread-safe!
class Workspace:
	"""Represents a virtual workspace that provides an overlay over a set of virtual documents"""
	root = "."
	documents = {}

	def __iter__(self):
		return iter(self.documents.items())

	def open(self, path, sanitized):
		if sanitized is False:
			path = sanitize(path)

		# Try the workspace overlay before the FS
		doc = self.get(path, True)
		if doc is None:
			return self.open_from_fs(path, True)
			
		return doc


	def open_with_content(self, path, content, sanitized):
		if sanitized is False:
			path = sanitize(path)

		doc = self.get(path, True)
		if doc is None:
			doc = Document()
			doc.uri = path
			doc.content = content

			self.count_lines(doc)
			self.documents[path] = doc

		return doc

	def open_from_fs(self, path, sanitized):
		if sanitized is False:
			path = sanitize(path)

		# Root relative paths
		if path.startswith("/") is False:
			rooted_path = os.path.join(self.root, path)
		else:
			rooted_path = path

		doc = Document()
		content = ""

		try:
			content = open(rooted_path).read()

		except IOError:
			echo("Could not read path '%s'" % rooted_path)

		doc.content = content

		self.count_lines(doc)
		self.documents[path] = doc
		return doc

	def get(self, path, sanitized):
		if sanitized is False:
			path = sanitize(path)

		doc = self.documents.get(path)
		if doc is not None:
			return doc

		return None
	
	def get_or_create(self, path, content, sanitized):
		if sanitized is False:
			path = sanitize(path)

		doc = self.documents.get(path, True)
		if doc is not None:
			return doc
		else:
			return self.open_with_content(path, content, True)

	def update(self, path, content, sanitized):
		if sanitized is False:
			path = sanitize(path)

		doc = self.get_or_create(path, content, True)
		doc.content = content

		self.count_lines(doc)
		return

	def count_lines(self, doc):
		doc.lines = doc.content.count("\n") + 1
		return

	def clear(self):
		self.documents.clear()
		return

	def unroot(self, path):
		unrooted = path
		if unrooted.startswith(self.root):
			prefix_len = len(self.root) + 1
			unrooted = unrooted[prefix_len:]

		return unrooted
