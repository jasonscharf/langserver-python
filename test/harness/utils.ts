import { IConnection, InitializeParams, InitializeResult, DidOpenTextDocumentParams } from "vscode-languageserver";

import * as Promise from "bluebird";
import * as fs from "fs";
import * as path from "path";
import * as child_process from "child_process";
import { JediHarness } from "./JediHarness";
import { JediMessage } from "./protocol";

export const didOpenTextDocument: DidOpenTextDocumentParams = {
	textDocument: {
		uri: "potato.py",
		languageId: "python",
		version: 1,
		text: fs.readFileSync("./test/data/potato.py").toString()
	}
}

export const getLogger = (prefix = "LS", connection?: IConnection) => {
	return (msg, ...extras) => {
		console.log(`[${prefix}]: ${msg}`);

		if (!connection) {
			return;
		}
		else {
			try {
				connection.console.log(msg);
			}
			catch (err) {
				console.error(`Error while logging: `, err);
			}
		}
	}
}

export function getInitParams() {
	const processId = 1;
	const params = {
		capabilities: {
		},
		processId,
		rootPath: path.join(process.cwd(), "./test/data")
	};
	return params;
}

export function getHarness(): Promise<JediHarness> {
	return new Promise<JediHarness>((resolve, reject) => resolve(new JediHarness()));
}

export function initHarness(params?: InitializeParams, harness?: JediHarness, ): Promise<JediMessage<InitializeResult>> {
	return (!harness ? getHarness() : Promise.resolve(harness))
		.then(harness => {
			if (!params) {
				params = getInitParams();
			}
			return harness.initialize(params);
		});
}

export function exec(cmd: string, args: string[] = []): Promise<any> {
	return new Promise((resolve, reject) => {
		child_process.exec(cmd, args, (error, stdout, stderr) => {
			if (error) {
				reject(error);
				return;
			}

			resolve(stdout);
			return;
		});
	});
}

export function execFile(file: string, args: string[] = []): Promise<any> {
	return new Promise((resolve, reject) => {
		child_process.execFile(file, args, (error, stdout, stderr) => {
			if (error) {
				reject(error);
				return;
			}

			resolve(stdout);
			return;
		});
	});
}
