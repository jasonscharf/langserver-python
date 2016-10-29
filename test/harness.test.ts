import * as Promise from "bluebird";
import * as mocha from "mocha";
import * as chai from "chai";
import * as fs from "fs";
import * as utils from "./../src/utils";
import * as constants from "./../src/constants";

import { InitializeParams, InitializeResult, DidOpenTextDocumentParams } from "vscode-languageserver";
import { JediHarness } from "./../src/lang/python/JediHarness";
import { JediMessage } from "./../src/lang/python/protocol";


import assert = require("assert");

const didOpenTextDocument: DidOpenTextDocumentParams = {
	textDocument: {
		uri: "potato.py",
		languageId: "python",
		version: 1,
		text: fs.readFileSync("./test/data/potato.py").toString()
	}
};

const log = utils.getLogger("harness.test");
const getInitParams = () => {
	const processId = 1;
	const params = {
		capabilities: {
		},
		processId,
		rootPath: "../test/data/",
	};
	return params;
};
const getHarness = () => new Promise<JediHarness>((resolve, reject) => resolve(new JediHarness()));
const initHarness = (params?: InitializeParams, harness?: JediHarness, ): Promise<JediMessage<InitializeResult>> => {
	return (!harness ? getHarness() : Promise.resolve(harness))
		.then(harness => {
			if (!params) {
				params = getInitParams();
			}
			return harness.initialize(params);
		});
};

describe("harness", () => {
	it("initializes and connects to ls-python", () => {
		return getHarness()
			.then(harness => {
				return harness.initialize(getInitParams())
					.then(initResponse => {
						const { id, result } = initResponse;
						const { capabilities } = result;

						assert.equal(id, 0);
						assert.equal(typeof result, "object");
						assert.equal(capabilities.hoverProvider, true);
						return harness;
					});
			})
			.then(harness => harness.exit())
			;
	});

	it("exits cleanly", () => {
		return getHarness()
			.then(harness => {
				return harness.initialize(getInitParams())
					.then(initResponse => {
						const { result } = initResponse;
						assert.equal(typeof result, "object");
					})
					.then(() => harness.exit())
					.then(codeOrSig => {
						log(`SIG: ` + codeOrSig);
						assert.equal(codeOrSig, "SIGTERM");
					})
					;
			});
	});

	it("doesn't explode when messages are queuing up", () => {
		return getHarness()
			.then(harness => {
				// Kick off the init sequence and then start firing a stream of messages, disregarding any ready state
				harness.initialize(getInitParams())
					.then(harness => {
						log(`Harness initialized`);
					});

				harness.onDidOpenTextDocument(didOpenTextDocument);
				harness.onDidOpenTextDocument(didOpenTextDocument);
				harness.onDidOpenTextDocument(didOpenTextDocument);
				harness.onDidOpenTextDocument(didOpenTextDocument);
				harness.onDidOpenTextDocument(didOpenTextDocument);

				return new Promise((resolve, reject) => {
					setTimeout(resolve, 1000);
				});
			});
	});
});
