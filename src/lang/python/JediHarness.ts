import * as Promise from "bluebird";
import {
	TextDocuments, TextDocument, Diagnostic, DiagnosticSeverity,
	InitializeParams, InitializeResult, TextDocumentPositionParams, TextDocumentContentChangeEvent,
	CompletionItem, CompletionItemKind, Definition, Hover, Location, ReferenceParams,
	DidChangeTextDocumentParams, DidChangeWatchedFilesParams, DidOpenTextDocumentParams, DidChangeConfigurationParams, DidCloseTextDocumentParams,
} from "vscode-languageserver"; // TODO: remove unused


import { JediServiceStdioWrapper } from "./JediServiceStdioWrapper";
import { LanguageServer, LanguageServerState } from "./../../lang-server/LanguageServer";
import { JediMessage } from "./protocol";
import { PythonWorkspace } from "./PythonWorkspace";
import { SourceSnapshot } from "./../../models/SourceSnapshot";
import { getLogger } from "./../../utils";

const log = getLogger("HARN");



/**
 * LSP Server that interacts with Jedi over a transport such as stdio or TCP/IP.
 */
export class JediHarness implements LanguageServer {
	protected _state = LanguageServerState.Uninitialized;
	protected _initResponse: JediMessage<InitializeResult>;
	protected _workspace: PythonWorkspace;
	protected _wrapper: JediServiceStdioWrapper;


	/**
	* Synchronous, fire-and-forget LSP init.
	*/
	onInitialize(params): InitializeResult {
		const { documents } = params;
		this.initialize(params);

		// Note: langserver-python.py also broadcasts these capabilities but is not used (because async)
		return {
			capabilities: {
				textDocumentSync: documents.syncKind,
				hoverProvider: true,
				definitionProvider: true,
				referencesProvider: true,
				/*
				workspaceSymbolProvider: true,
				*/
			}
		}
	}

	initialize(params: InitializeParams): Promise<JediMessage<InitializeResult>> {
		// TODO: Note: This will need to be revisited for integration in the backend, and perhaps a cached promise should be returned on overlapping init calls 
		if (this._state === LanguageServerState.Initialized) {
			return Promise.resolve(this._initResponse);
		}

		// TODO: Test multiple inits re: workspace lifecycle and in the context of the Sourcegraph backend
		log(`Initializing...`);

		this._state = LanguageServerState.Uninitialized;
		this._workspace = new PythonWorkspace();
		this._wrapper = new JediServiceStdioWrapper();

		// TODO: Note: This is where pre-init could be specified to the wrapper.
		// TODO: Also, since LSP init is not invoked async, this could be a notify. 
		return this._wrapper.init()
			.then(() => this._wrapper.send<InitializeParams, InitializeResult>("initialize", params))
			.then(response => {
				this._state = LanguageServerState.Initialized;
				return this._initResponse = response;
			})
			;
	}

	exit(): Promise<string | number> {
		if (!this._wrapper) {
			return Promise.reject(new Error("Harness was not running"));
		}
		else {
			return this._wrapper.exit();
		}
	}

	getPosFromLineCharPair(source: SourceSnapshot, line: number, char: number): number {
		return 0;
	}

	getWorkspaceSources(): SourceSnapshot[] {
		return [];
	}

	onCompletion(params): CompletionItem[] {
		return [];
	}

	onDidChangeContent(params: any): void {
	}

	onDidChangeConfiguration(params: DidChangeConfigurationParams): void {
	}

	onDidOpenTextDocument(params: DidOpenTextDocumentParams): void {

		/* 
		From LSP spec:
		> The document open notification is sent from the client to the server to signal newly opened text documents.
		> The document's truth is now managed by the client and the server must not try to read the document's truth using the document's uri.
		*/

		this._wrapper.notify("textDocument/didOpen", params);
	}

	onDefinition(params: TextDocumentPositionParams): Definition {
		return null;
	}

	onReferences(params: ReferenceParams): Location[] {
		// # TODO: Prebuild symbol refs on the python side, init them when docs are opened and notify em back for sync resolution
		return [];
	}

	onDidChangeWatchedFiles(change: DidChangeWatchedFilesParams): void {

	}

	onCompletionResolve(item: CompletionItem): CompletionItem {
		return null;
	}

	onDidChangeTextDocument(params: DidChangeTextDocumentParams): void {
	}

	onDidCloseTextDocument(params: DidCloseTextDocumentParams): void {

	}

	onHover(params: TextDocumentPositionParams) {

	}
}
