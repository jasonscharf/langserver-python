'use strict';

import * as net from 'net';
import * as path from 'path';
import * as Promise from 'bluebird';

import { workspace, Disposable, ExtensionContext, Uri } from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient';


export function launchCommand(context: ExtensionContext, name: string, command: string, documentSelector: string | string[]): Thenable<LanguageClient> {
	const client = startLangServerCommand(name, command, documentSelector);
	context.subscriptions.push(client.start());
	return client.onReady()
		.then(() => client)
		;
}

export function launchTcp(context: ExtensionContext, name: string, host: string, port: number, documentSelector: string | string[]): Thenable<LanguageClient> {
	const client = startLangServerTCP(name, host, port, documentSelector);
	context.subscriptions.push(client.start());
	return client.onReady()
		.then(() => client)
		;
}


function startLangServerCommand(name: string, command: string, documentSelector: string | string[]): LanguageClient {
	const serverOptions: ServerOptions = {
		command: command,
	};
	const clientOptions: LanguageClientOptions = {
		documentSelector: documentSelector,
	}

	return new LanguageClient(name, serverOptions, clientOptions);
}

function startLangServerTCP(name: string, host: string, port: number, documentSelector: string | string[]): LanguageClient {
	const serverOptions: ServerOptions = function () {
		return new Promise((resolve, reject) => {
			const client = new net.Socket();
			client.connect(port, host, () => {
				resolve({
					reader: client,
					writer: client,
				});
			});
		});
	}

	const clientOptions: LanguageClientOptions = {
		documentSelector: documentSelector,
	}

	return new LanguageClient(`${name} @ ${host}:${port})`, serverOptions, clientOptions);
}

function startLangServerIPC(name: string, serverModule: string, context: ExtensionContext, documentSelector: string | string[]) {
	const debugOptions = { execArgv: ['--nolazy', '--debug=6004'] };

	// If the extension is launched in debug mode then the debug server options are used
	// Otherwise the run options are used
	const serverOptions: ServerOptions = {
		run: { module: serverModule, transport: TransportKind.ipc },
		debug: { module: serverModule, transport: TransportKind.ipc, options: debugOptions }
	}

	// Options to control the language client
	const clientOptions: LanguageClientOptions = {
		// Register the server for plain text documents
		documentSelector,
		synchronize: {
			// Synchronize the setting section 'languageServerExample' to the server
			configurationSection: 'languageServerExample',
			fileEvents: workspace.createFileSystemWatcher('**/.clientrc')
		}
	}

	return new LanguageClient(name, serverOptions, clientOptions).start();
}

function startCommand(name: string, command: string, context: ExtensionContext, ...args: any[]) {
	const client = new LanguageClient(
		name,
		{
			command,
			args: [
				'-mode=stdio',

				// Uncomment for verbose logging to the vscode
				// 'Output' pane and to a temporary file:
				//
				// '-trace', '-logfile=/tmp/langserver-go.log',
			],
		},
		{
			documentSelector: ['go'],
			uriConverters: {
				// Apply file:/// scheme to all file paths.
				code2Protocol: (uri: Uri): string => (uri.scheme ? uri : uri.with({ scheme: 'file' })).toString(),
				protocol2Code: (uri: string) => Uri.parse(uri),
			},
		}
	);

	// Update GOPATH, GOROOT, etc., when config changes.
	updateEnvFromConfig();
	context.subscriptions.push(workspace.onDidChangeConfiguration(updateEnvFromConfig));
	return client;
}

function updateEnvFromConfig() {
	const conf = workspace.getConfiguration('go');
	if (conf['goroot']) {
		process.env.GOROOT = conf['goroot'];
	}
	if (conf['gopath']) {
		process.env.GOPATH = conf['gopath'];
	}
}