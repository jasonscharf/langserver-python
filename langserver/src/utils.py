import sys
import urllib

def echo(str):
	sys.stderr.write(str + "\n")
	return

def sanitize(uri):
	if uri.startswith("file:///"):
		uri = urllib.unquote(uri[7:])
	return uri

def normalize_vsc_uri(path):
	ret = "file://%s" % urllib.quote(path.replace("\\", "/"))
	return ret
