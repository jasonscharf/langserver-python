import * as mocha from "mocha";
import * as chai from "chai";
import * as constants from "./../src/constants";
import * as utils from "./../src/utils";

import assert = require("assert");

const log = utils.getLogger();
const getResults = (line: number, col: number, type = "hover", path = "./test/data/rutabaga.py") => {
	return utils.execFile(constants.Python.DEFAULT_PYTHON3_PATH, [
		constants.Python.LANGSERVER_PATH,
		"--path", path,
		"--line", line.toString(),
		"--column", col.toString(),
		type]);
};

describe("jedi", () => {
	it.skip("responds to basic messages", () => {
		return getResults(1, 7, "definition")
			.then(result => {
				assert.ok(result != null);
				assert.ok(result.length > 0);
			});
	});

	it.skip("provides definitions", () => {
		return getResults(8, 9, "definition")
			.then(result => {
				const definition = JSON.parse(result);
				assert.equal(definition.line, 1, "the line should be 1");
				assert.equal(definition.column, 6, "the column should be 6");
			});
	});

	// TODO: Changing the column to 9 seems to yield incorrect results. Why?
	it.skip("provides hover", () => {
		return getResults(8, 10, "hover")
			.then(result => {
				// Some Results from Jedi have trailing newlines.
				const cleaned = result.replace(/[\r\n]+$/, "");
				const expected = "Rutabaga(self)";
				assert.ok(cleaned === expected, `expected '${expected}'`);
			});
	});

	it.skip("provides references", () => {
		return getResults(1, 10, "references")
			.then(result => {
				const refs: { line: number, column: number }[] = JSON.parse(result);
				const lines = refs.map(ref => ref.line);
				const columns = refs.map(ref => ref.column);

				// [line, col]
				const expected = [[8, 7], [10, 14], [11, 13]];

				assert.equal(refs.length, expected.length, `expected ${expected.length} references`)

				refs.forEach((ref, i) => {
					const { line, column } = ref;
					const [expectedLine, expectedColumn] = expected[i];

					assert.equal(line, expectedLine, `expected ref ${i} to be at line ${expectedLine} but was at ${line}`);
					assert.equal(column, expectedColumn, `expected ref ${i} to be at column ${expectedColumn} but was at ${column}`);
				});
			});
	});

	// Note: Just for testing
	it.skip("provides completions", () => {
		return getResults(8, 9, "completions")
			.then(result => {
				const definition = JSON.parse(result);
				assert.equal(definition.line, 1, "the line should be 1");
				assert.equal(definition.column, 6, "the column should be 6");
			});
	});

	// TODO: Enable once "workspace/symbol" is supported
	it.skip("provides workspace symbols", () => {

	});
});
