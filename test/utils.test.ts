import * as mocha from "mocha";
import * as chai from "chai";
import * as constants from "./harness/constants";
import * as utils from "./harness/utils";

import assert = require("assert");


describe("utils", () => {
	describe("exec", () => {
		it("can launch a child process", () => {
			return utils.exec("echo hello")
				.then(result => {
					assert.ok(result != null);
				});
		});

		it("can launch a Python process from PATH or CWD", () => {
			return utils.execFile(`python`, ["-c", "print 'hello world'"])
				.then(result => {
					assert.ok(result != null);
				});
		});
	});
});
