# Python Language Server

Language server which talks LSP via JSON-RPC for Python.
and Python 3 (script to call [Jedi](https://jedi.readthedocs.io/en/latest/index.html)) with limited set of LSP methods currently implemented.

## Getting Started

As in early stage, this only works with our [vscode-client](https://github.com/sourcegraph/sourcegraph/tree/master/lang/vscode-client) extension, and not field tested for integration with main Sourcegraph app.

Make sure you have installed:

1. Go
2. Python3
3. Jedi

To debug with VSCode, you need to:

1. `go get github.com/sourcegraph/langserver-python`
2. Symbolic link `./src/langserver-python.py` to a place inside `$PATH` (e.g. `$GOPATH/bin`)
3. Follow the [vscode-client README](https://github.com/sourcegraph/langserver/tree/master/vscode-client)