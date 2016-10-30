import * as Promise from "bluebird";
import * as mocha from "mocha";
import * as chai from "chai";

import * as constants from "./harness/constants";
import { JediHarness } from "./harness/JediHarness";
import { JediMessage } from "./harness/protocol";
import { getLogger, getHarness, getInitParams, didOpenTextDocument } from "./harness/utils";

import assert = require("assert");

const log = getLogger("harness.test");


describe("workspace", () => {
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
});
