import sys
import urllib

from os.path import expanduser


def echo(str):
	sys.stderr.write(str + '\n')
	home = expanduser('~')
	with open(home + '/log.text', 'a') as myfile:
		myfile.write(str + '\n')

	return

def sanitize(uri):
	if uri.startswith('file:///'):
		uri = urllib.unquote(uri[7:])

	return urllib.quote(uri.replace('\\', '/'))

def normalize_vsc_uri(path):
	uri = 'file:///%s' % urllib.quote(path.replace('\\', '/'))

	if uri.startswith('file:////') is True:
		uri = uri.replace('file:////', 'file:///')

	return uri
