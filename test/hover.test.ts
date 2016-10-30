import * as Promise from "bluebird";
import * as mocha from "mocha";
import * as chai from "chai";
import * as fs from "fs";
import { InitializeParams, InitializeResult, DidOpenTextDocumentParams, TextDocumentPositionParams, Hover } from "vscode-languageserver";

import * as constants from "./harness/constants";
import { JediHarness } from "./harness/JediHarness";
import { JediMessage } from "./harness/protocol";
import { getLogger, getHarness, getInitParams, didOpenTextDocument } from "./harness/utils";

import assert = require("assert");

const log = getLogger("test.hover");


describe("hover", () => {
	it("hover works", () => {
		return getHarness()
			.then(harness => {
				return harness.initialize(getInitParams())
					.then(() => {
						harness.onDidOpenTextDocument(didOpenTextDocument);

						const params: TextDocumentPositionParams = {
							textDocument: {
								uri: "rutabaga.py"
							},
							position: {
								line: 7,
								character: 0
							}
						}

						return harness.send<Hover>("textDocument/hover", params)
							.then(env => {
								const { result } = env;
								const { contents, range } = result;

								assert.ok(contents != null);
								assert.ok(contents != null);
							})
							.then(() => harness.exit())
					})
			})
			;
	});
});
