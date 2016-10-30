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
		return self.documents.iteritems()

	def open(self, path):
		path = sanitize(path)
		doc = self.get(path)
		if doc is None:
			return self.open_from_fs(path)
		else:
			return doc

	def open_with_content(self, path, content):
		path = sanitize(path)
		doc = self.get(path)
		if doc is None:
			echo("Add script '{}'".format(path))
			doc = Document()
			doc.uri = path
			doc.content = content

			self.count_lines(doc)
			self.documents[path] = doc

		return doc

	def open_from_fs(self, path):
		path = sanitize(path)
		rooted_path = os.path.join(self.root, path)
		doc = Document()
		try:
			content = open(rooted_path).read()
		except IOError:
			content = ""

		doc.content = content

		self.count_lines(doc)
		self.documents[path] = doc
		return doc

	def get(self, path):
		path = sanitize(path)
		doc = self.documents.get(path)
		if doc is not None:
			echo("Found existing doc '{}'".format(path))
			return doc

		return None
	
	def get_or_create(self, path, content=""):
		path = sanitize(path)
		doc = self.documents.get(path)
		if doc is not None:
			return doc
		else:
			return self.open_with_content(path, content)

	def update(self, path, content):
		path = sanitize(path)
		echo("Update {}".format(path))
		doc = self.get_or_create(path)
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
