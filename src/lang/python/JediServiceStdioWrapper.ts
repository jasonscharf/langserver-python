
import * as child_process from "child_process";
import * as Promise from "bluebird";
import * as net from "net";
import * as readline from "readline";
import * as constants from "./../../constants";
import * as utils from "./../../utils";

import { JediResponse } from "./protocol";
import { LanguageServer } from "./../../lang-server/LanguageServer";
import { SourceSnapshot } from "./../../models/SourceSnapshot";

const log = utils.getLogger("LSW");
const pylog = utils.getLogger("PY");

// Note: These match values in `langserver-python.py'
const DEFAULT_HOST = "localhost";
const DEFAULT_PORT = 9999;


Promise.onPossiblyUnhandledRejection(err => console.error("Unhandled rejection: ", err));


/**
 * Wraps a Python process running Jedi and communicates with it over stdio. See 'tooling/langserver-python.py'.
 */
export class JediServiceStdioWrapper {
	// TODO: Factor out into a cleaner "transport" in order to swap in different clients, i.e. vscode-jsonrpc and such
	protected _langserverProc: child_process.ChildProcess;
	protected _requestCallbacks: { [id: string]: Function[] } = {};
	protected _initPromise: Promise<void>;
	protected _nextId = 0;

	init(): Promise<void> {
		if (this._initPromise) {
			return this._initPromise;
		}
		else {
			this._initPromise = this._startJediServerProcess()
				.then(() => this._connectToJediLSPServer())
				.then(() => void 0)
				.catch(err => {
					log(`Error received while booting Jedi service wrapper: ` + err);
				});
			;
			return this._initPromise;
		}
	}

	notify<T, U>(method: string, params?: T): void {
		this._send<T, U>(true, method, params);
		return;
	}

	send<T, U>(method: string, params?: T): Promise<JediResponse<U>> {
		return this._send<T, U>(false, method, params);
	}

	protected _send<T, U>(notification: boolean, method: string, params?: T): Promise<JediResponse<U>> {
		const id = this._nextId++;

		return this._initPromise
			.then(() => {
				return new Promise<JediResponse<U>>((resolve, reject) => {
					const envelope = {
						"jsonrpc": "2.0",
						method,
						params,
					};

					if (!notification) {
						envelope["id"] = id;
					}

					const serialized = JSON.stringify(envelope);
					const len = serialized.length;
					const message = `Content-Length: ${len}\r\n\r\n${serialized}`;

					// Register the callback after a successful send
					this._langserverProc.stdin.write(new Buffer(message), (err, result) => {
						if (err) {
							return Promise.reject(err);
						}
						else if (!notification) {
							this.registerCallback(id, response => resolve(response));
						}
					});
				})
					.catch(err => {
						console.error(err);
					});
			});
	}

	fireCallbacks<T>(payload: JediResponse<T>): void {
		const key = payload.id;
		const callbacks = this._requestCallbacks[key];
		if (!callbacks) {
			return;
		}
		else {
			delete this._requestCallbacks[key];
			callbacks.forEach((cb, i) => {
				try {
					cb(payload);
				}
				catch (err) {
					log(`Callback ${i} for request ${key}`);
				}
			});
		}
	}

	registerCallback(requestId: number, callback: <T>(result: JediResponse<T>) => void): void {
		const key = requestId.toString();
		const callbacks = this._requestCallbacks[key] || (this._requestCallbacks[key] = []);
		callbacks.push(callback);
	}

	shutdown() {
		log(`Received 'shutdown'`);
	}

	exit(): Promise<string | number> {
		log(`Received 'exit'. Shutting down process...`);
		return this._shutdownJediServerProcess();
	}

	protected _handleStdoutData(data: Buffer) {
		const str = data.toString();
		if (!/^\d+!/.test(str)) {
			throw new Error(`Didn't read enough ('${str}')`)
		}

		const bufferLen = data.byteLength;
		const ix = str.indexOf("!");
		const preamble = str.slice(0, ix);
		const len = parseInt(preamble);
		const readTo = ix + 1 + len;
		const payloadRaw = str.slice(ix + 1, readTo);
		let payload: JediResponse<any>;
		try {
			payload = JSON.parse(payloadRaw);
		}
		catch (err) {
			log(`Error decoding JSON (raw body follows error):\n${err}\n`);
			log(payloadRaw);
		}

		// Fire any registered callbacks with the inner LSP result (i.e. actual definitions, symbols, references, etc)
		this.fireCallbacks(payload);

		if (readTo < bufferLen) {
			log(`Received multiple messages`);
			this._handleStdoutData(data.slice(readTo));
		}
	}

	protected _handleStderrData(data: Buffer) {
		pylog(data);
	}

	protected _startJediServerProcess(): Promise<void> {
		return new Promise<void>((resolve, reject) => {
			if (this._langserverProc) {
				return Promise.resolve();
			}

			log(`Spawning Jedi process...`);
			this._langserverProc = child_process.spawn(constants.Python.DEFAULT_PYTHON3_PATH, ["-u", constants.Python.LANGSERVER_PATH, "serve"]);

			// TODO: IMPORTANT: This is uber gross. Wait for a stream readable event or something.
			setTimeout(resolve, 250);
			return;
		});
	}

	protected _connectToJediLSPServer(): Promise<void> {
		log(`Attaching to ${constants.Python.LANGSERVER_PATH}...`)
		return new Promise<void>((resolve, reject) => {
			this._langserverProc.stdout.on("data", data => this._handleStdoutData(<Buffer>data));
			this._langserverProc.stderr.on("data", data => this._handleStderrData(<Buffer>data));
			this._langserverProc.on("close", (code, signal) => {
				log(`Jedi process exits with code ${code !== null ? code : signal}`);
				if (code != null && code !== 0) {
					throw new Error(`Jedi process exit with nonzero code ${code}`);
				}
			});
			resolve();
		});
	}

	protected _shutdownJediServerProcess(): Promise<string | number> {
		return new Promise<string | number>((resolve, reject) => {
			if (!this._langserverProc) {
				throw new Error("JediServiceWrapper not running");
			}

			log(`Killing Jedi process...`);
			this._langserverProc.on("close", (code: number, signal: string) => resolve(code !== null ? code : signal));
			this._langserverProc.kill();
		});
	}
}
