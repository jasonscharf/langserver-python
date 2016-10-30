import * as Promise from "bluebird";
import * as mocha from "mocha";
import * as chai from "chai";
import * as fs from "fs";
import { InitializeParams, InitializeResult, DidOpenTextDocumentParams } from "vscode-languageserver";

import * as constants from "./harness/constants";
import { JediHarness } from "./harness/JediHarness";
import { JediMessage } from "./harness/protocol";
import { getLogger, getHarness, getInitParams, didOpenTextDocument } from "./harness/utils";

import assert = require("assert");

const log = getLogger("test.harness");


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
					setTimeout(() => harness.exit().then(resolve), 1000);
				});
			})
	});
});
