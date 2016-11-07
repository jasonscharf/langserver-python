import * as mocha from 'mocha';
import * as assert from 'assert';
import * as path from 'path';
import * as vscode from 'vscode';
import { TextDocumentPositionParams, TextDocumentIdentifier } from 'vscode-languageclient';

import * as globals from '../../globals';


export function exec(command: string, uri: vscode.Uri, ...args: any[]): Thenable<any> {
	const executeCommand = (textDocument?: vscode.TextDocument) => {
		if (textDocument) {
			return vscode.commands.executeCommand(command, textDocument.uri, ...args);
		}
		else {
			return vscode.commands.executeCommand(command, ...args);
		}
	};

	const ext = vscode.extensions.getExtension("sourcegraph.python").activate();

	// Workaround for the fact that the promise(like) returned from `activate` does NOT indicate that the extension is 'ready'.
	// This leads to silent failures, although sometimes results are produced.
	// Unclear as to how 'onReady' is intended to be used for testing - it is not avilable on the extension instance itself,
	// and the `ExtensionContext` for the extension does not appear to be available here either.
	return globals.event.onReady()
		.then(() => {
			if (uri) {
				return vscode.workspace.openTextDocument(uri)
					.then(executeCommand)
			}
			else {
				return executeCommand()
			}
		});
}