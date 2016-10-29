import {
	TextDocuments, TextDocument, Diagnostic, DiagnosticSeverity,
	InitializeParams, InitializeResult, TextDocumentPositionParams, TextDocumentContentChangeEvent,
	CompletionItem, CompletionItemKind, Definition, Hover, Location, ReferenceParams,
	DidChangeTextDocumentParams, DidChangeWatchedFilesParams, DidOpenTextDocumentParams, DidChangeConfigurationParams, DidCloseTextDocumentParams,
} from "vscode-languageserver";


import { SourceSnapshot } from "./../models/SourceSnapshot";


export interface LanguageServerArgs {
	workspaceRoot: string;
	documents: TextDocuments;
}

export const enum LanguageServerState {
	Uninitialized,
	Initializing,
	Initialized,
	Shutdown,
}

// TODO: Sync w/ IConnection
// TODO: workspace/symbols + shutdown 
export interface LanguageServer {
	getPosFromLineCharPair(source: SourceSnapshot, line: number, char: number): number;
	getWorkspaceSources(): SourceSnapshot[]

	// Actual LSP methods
	onInitialize(params): InitializeResult;
	onCompletion(params): CompletionItem[];
	onDidChangeContent(params: any): void;
	onDidChangeConfiguration(params: DidChangeConfigurationParams): void;
	onDidOpenTextDocument(params: DidOpenTextDocumentParams): void;
	onDefinition(params: TextDocumentPositionParams): Definition;
	onReferences(params: ReferenceParams): Location[];
	onDidChangeWatchedFiles(change: DidChangeWatchedFilesParams): void;
	onCompletionResolve(item: CompletionItem): CompletionItem;
	onDidChangeTextDocument(params: DidChangeTextDocumentParams): void;
	onDidCloseTextDocument(params: DidCloseTextDocumentParams): void;
	onHover(params: TextDocumentPositionParams)
}
