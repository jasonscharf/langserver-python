import { IConnection } from "vscode-languageserver";

import * as child_process from "child_process";
import * as Promise from "bluebird";


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

export function getLogger(prefix = "LS", connection?: IConnection) {
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
