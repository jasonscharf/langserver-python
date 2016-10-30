import sys
import urllib

def echo(str):
	sys.stderr.write(str + "\r\n")
	return

def sanitize(uri):
	if uri.startswith("file:///"):
		uri = urllib.unquote(uri[8:])
	
	return uri

def normalize_vsc_uri(path):
	return "file:///%s" % urllib.quote(path.replace("\\", "/"))
