import * as rpc from "vscode-jsonrpc";
import * as net from "net";

import { InitializeParams, InitializeResult, DidOpenTextDocumentParams } from 'vscode-languageserver';
import { LanguageClient, TextDocumentPositionParams, TextDocumentIdentifier } from 'vscode-languageclient';

const logger: rpc.Logger = {
    error: (message: string) => { },
    warn: (message: string) => () => { },
    info: (message: string) => () => { },
    log: (message: string) => () => { },
};



export class Connection {
    private _conn: rpc.ClientMessageConnection;
    private _input: NodeJS.ReadableStream;
    private _output: NodeJS.WritableStream;
    private _socket: net.Socket;


    createConnection(input: NodeJS.ReadableStream, output: NodeJS.WritableStream) {
        this._conn = rpc.createClientMessageConnection(new rpc.StreamMessageReader(input), new rpc.StreamMessageWriter(output), logger);
        const initializeParams: InitializeParams = {
            processId: process.pid,
            rootPath: "file:///",
            capabilities: {
            },
        };

        this._conn.onClose(() => {
            console.log(`Connection closed`);
        });

        this._conn.listen();
        return this._conn;
    }

    send(method: string, params: any) {
        return this._conn.sendRequest({ method }, params);
    }

    notify(method: string, params: any) {
        return this._conn.sendNotification({ method }, params);
    }

    hover(uri: string, line: number, character: number) {
        const hoverParams: TextDocumentPositionParams = {
            textDocument: {
                uri,
            },
            position: {
                line,
                character,
            }
        };

        return this.send("textDocument/hover", hoverParams);
    }

    didOpen(uri: string, text: string, languageId = "python", version = 1) {

        // Note that version isn't being incremented. The LSP server doesn't care about it and makes a reasonable assumption that it's always valid.
        const didOpenParams: DidOpenTextDocumentParams = {
            textDocument: {
                uri,
                languageId,
                text,
                version,
            }
        };

        return this.notify("textDocument/didOpen", didOpenParams);
    }

    definition() {

    }

    connect(host: string, port: number, initializeParams = DEFAULT_INITIALIZE_PARAMS) {
        const options = { host, port };

        this._socket = net.connect(options);
        this.createConnection(this._socket, this._socket);
        return this._conn.sendRequest({ "method": "initialize" }, initializeParams);
    }

    close() {
        this._socket.end();
        this._socket.destroy();
        return this._conn.dispose();
    }
}
var DEFAULT_INITIALIZE_PARAMS: InitializeParams = {
    processId: process.pid,
    rootPath: "file:///",
    capabilities: {
    },
};
