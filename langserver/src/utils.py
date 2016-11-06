import re
import sys
import urllib


def echo(str):
	# sys.stderr.write(str + '\n')
	return

def sanitize(uri):
	uri = uri.strip()

	if uri.startswith('file:///'):
		uri = uri[7:]

	uri = urllib.unquote(uri)
	uri = uri.replace("\\", '/')

	# Strip leading slash from absolute NTFS-style paths containing a drive letter, i.e. '/c:/projects/' => 'c:/projects/''
	if uri.startswith('/') and re.match('^\/\w:', uri) is not None:
		uri = uri[1:]

	return uri

def normalize_vsc_uri(path):
	uri = path.replace('\\', '/')
	uri = urllib.quote(uri)

	if uri.startswith('/'):
		uri = 'file://%s' % uri
	else:
		uri = 'file:///%s' % uri

	return uri
