/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';
import {
	IPCMessageReader, IPCMessageWriter,
	createConnection, IConnection, TextDocumentSyncKind,
	TextDocuments, TextDocument, Diagnostic, DiagnosticSeverity,
	InitializeParams, InitializeResult, TextDocumentPositionParams,
	CompletionItem, CompletionItemKind
} from "vscode-languageserver";

import { LanguageServer } from "./src/lang-server/LanguageServer";
import { JediHarness } from "./src/lang/python/JediHarness";
import { getLogger } from "./src/utils";

const log = getLogger("server");

// Create a logger and connection for the server. The connection uses Node's IPC as a transport
const connection: IConnection = createConnection(new IPCMessageReader(process), new IPCMessageWriter(process));
const harness: LanguageServer = new JediHarness();

// Create a simple text document manager. The text document manager
// supports full document sync only
const documents: TextDocuments = new TextDocuments();


// Make the text document manager listen on the connection
// for open, change and close text document events
documents.listen(connection);


// After the server has started the client sends an initilize request. The server receives
// in the passed params the rootPath of the workspace plus the client capabilites. 
connection.onInitialize((params): InitializeResult => {
	const workspaceRoot = params.rootPath || ".";
	return harness.onInitialize({
		workspaceRoot,
		documents,
	});
});

// The content of a text document has changed. This event is emitted
// when the text document first opened or when its content has changed.
documents.onDidChangeContent((change) => {
	harness.onDidChangeContent(change);
});

// The settings have changed. Is send on server activation
// as well.
connection.onDidChangeConfiguration(change => harness.onDidChangeConfiguration(change));

connection.onDidOpenTextDocument(params => {
	harness.onDidOpenTextDocument(params);
});
connection.onHover(params => harness.onHover(params));
connection.onDefinition(params => harness.onDefinition(params));
connection.onReferences(params => harness.onReferences(params));
connection.onDidChangeTextDocument(params => harness.onDidChangeTextDocument(params));
connection.onDidChangeWatchedFiles(change => harness.onDidChangeWatchedFiles(change));

// Not supported but plumbed anyways
connection.onCompletionResolve(item => harness.onCompletionResolve(item));
connection.onDidCloseTextDocument(params => harness.onDidCloseTextDocument(params));

// Listen on the connection
connection.listen();
