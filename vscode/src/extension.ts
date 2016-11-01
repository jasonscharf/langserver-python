/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';

import * as net from 'net';

import { Disposable, ExtensionContext, Uri, workspace } from 'vscode';
import { LanguageClient, LanguageClientOptions, SettingMonitor, ServerOptions, ErrorAction, ErrorHandler, CloseAction, TransportKind } from 'vscode-languageclient';

export function activate(context: ExtensionContext) {
	const c = new LanguageClient(
		'langserver-python',
		{
			command: 'langserver-python',
			args: [
				'--stdio',
			],
			options: {
				env: {
					"PYTHONUNBUFFERED": 1,
				}
			}
		},
		{
			documentSelector: ['python'],
		}
	);
	context.subscriptions.push(c.start());
}
