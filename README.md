# Python Language Server + VS Code extension

VS Code extension and language server which talks [LSP](https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md) via JSON-RPC. Runs in Python 3.

The `./vscode` directory contains a [Visual Studio Code](https://code.visualstudio.com) extension that provides Python language support using the Language Server in the `./langserver` directory.

**Note:** You can currently launch the VS Code extension from the parent (root) folder of the repo _if it has already been built_, i.e. you have already run `tsc` or are using `tsc -w` in `./vscode/`. This is just for convenience at this point but may change.

**Note:** If you're developing against the extension, you should open that workspace (`./vscode`) in VS Code.

## Getting Started

### Requirements

1. Python3
2. Jedi
3. Visual Studio Code if you want to debug tests or the extension itself

### Testing and Debugging

1. `go get github.com/sourcegraph/langserver-python` (**Note: use the address of this fork for now - instructions below assume this fork is used!**)
2. `chmod +x` and symbolic link `langserver/src/langserver-python.py` to a place inside `$PATH` (e.g. `$GOPATH/bin`)
3. To **test**, navigate into './vscode', install, test, and launch:

        cd vscode
        npm install
        npm test

4. To **debug**, cd into the 'vscode' dir and:

        code .
        # hit F5, note that you can run the ext. itself or its tests


## Notes

  - All tests are run in the context of the VS Code extension for now. This is in order to test as close to the real world situation as possible.

  - If you run into issues with Python3 and `pip` or `jedi` on Ubuntu, please see [this useful SO thread](http://stackoverflow.com/questions/10763440/how-to-install-python3-version-of-package-via-pip-on-ubuntu)


### Performance
  - Jedi itself performs quite well, although still subject to typical runtime (Python) concerns
  - Logging output - even basic stdio logging - can have a very noticable impact on performance 
  - Raw, 'dumb' serialization into strings/buffers for JSON responses may yield tangible gains when schema is known and limited in complexity, e.g. _LSP_
  - See _Future Enhancements_ below for other possible perf. gains
  - IO, as always, is the biggest bottleneck, but particularly with Python. Preloading virtual workspaces from [V]FS into 'warm' processes should yield tangible benefits.

### Known Issues

  - In this version, `textDocument/hover` uses Jedi's `usages` facility (like the alpa), although this should change to use Jedi's proper `definitions` facility, as it yields false positives on hover at the boundaries of textual symbol spans, but is a cheapish way to accomplish hover functionality.
    - Note: Should test in Python 3 runtime vs Python 2 for perf differences

  - Jedi can run into an issue w/ a corrupted cache. See [here](https://github.com/davidhalter/jedi-vim/issues/251). As noted in the thread, this may be a concurrency issue, e.g. running multiple instances of VS Code w/ active Python extensions
    - I only encountered this once and in thousands of runs of Jedi and with dual instances of VS Code running, sometimes with other Python extensions running (**-jscharf**) 
      - `rm -rf ~/.cache/jedi` does indeed fix this issue
      - In a containerized environment, this may be so ephemeral as to be a non-issue, however, sporadic (seemingly _very sporadic_) failures in long-term CI could be red herrings.


### Future enhancements
  - Use `definitions` instead of `usages` for hover to remove false positives (simple change)
  - Proper support for type annotations, generic types, type aliases, et cetera
  - Python as a language is fairly simple to handle and parse from both the lexical and semantic viewpoints, and raw ASTs are available from the `compile` builtin
  - Symbolic in resolution in most Python apps is simple enough that a separate, more performant language such as Go could actually resolve refs, defs, and even symbols by offhanding ASTs to them for specific, targeted resolution concerns.
    - This may yield significant benefits where concerns such as type checking and completeness may be secondary to basic symbolic linking and human-driven code search