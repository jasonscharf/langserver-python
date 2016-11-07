import * as mocha from 'mocha';
import * as assert from 'assert';
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import * as globals from '../../globals';

import { Location, } from 'vscode-languageclient';
import { exec } from '../utils/exec';

const root = vscode.workspace.rootPath;
const dataPath = "../../src/test/data";
const filePath = 'definitions.py'

console.log("Workspace root is " + root)

export function definition(filename: string, line: number, char: number): Thenable<Location[]> {
	const pos = new vscode.Position(line, char);
	const uri = vscode.Uri.file(path.join(root, dataPath, filename));
	return exec("vscode.executeDefinitionProvider", uri, pos);
}

suite('definitions', () => {
	const commonAssert = (locs: Location[]) => {
		assert.ok(locs, 'received response from textDocument/definition');
		assert.ok(locs.length > 0, 'expected at least one definition response');
		return locs[0];
	};

	test('resolved in same folder', () => {
		return definition('definitions/qualified-imports.py', 3, 12)
			.then(commonAssert)
			.then(loc => {
				assert.ok(/a\.py$/.test(loc.uri.toString()), 'def should be in a.py');
				assert.equal(loc.range.start.line, 0, `def should be on line 0`);
				assert.equal(loc.range.start.character, 6, `def should be on char 6`);
			});
	});

	test('resolved in subfolder bearing __init__.py', () => {
		return definition('definitions/qualified-imports.py', 4, 17)
			.then(commonAssert)
			.then(loc => {
				assert.ok(/b\.py$/.test(loc.uri.toString()), 'def should be in b.py');
				assert.equal(loc.range.start.line, 0, `def should be on line 0`);
				assert.equal(loc.range.start.character, 6, `def should be on char 6`);
			});
	});

	test('resolved for bound import symbols', () => {
		return definition('definitions/bound.py', 0, 15)
			.then(commonAssert)
			.then(loc => {
				assert.ok(/a\.py$/.test(loc.uri.toString()), 'def should be in a.py');
				assert.equal(loc.range.start.line, 0, `def should be on line 0`);
				assert.equal(loc.range.start.character, 6, `def should be on char 6`);
			});
	});

	test('resolved for bound import symbols from qualified imports', () => {
		return definition('definitions/bound.py', 1, 24)
			.then(commonAssert)
			.then(loc => {
				assert.ok(/b\.py$/.test(loc.uri), 'def should be in b.py');
				assert.equal(loc.range.start.line, 0, `def should be on line 0`);
				assert.equal(loc.range.start.character, 6, `def should be on char 6`);
			});
	});

	test('resolved for aliased import symbols', () => {
		return definition('definitions/aliased.py', 0, 24)
			.then(commonAssert)
			.then(loc => {
				assert.ok(/a\.py$/.test(loc.uri), 'def should be in a.py');
				assert.equal(loc.range.start.line, 0, `def should be on line 0`);
				assert.equal(loc.range.start.character, 6, `def should be on char 6`);
			});
	});

	test('resolved for aliased import symbols from qualified imports', () => {
		return definition('definitions/aliased.py', 1, 24)
			.then(commonAssert)
			.then(loc => {
				assert.ok(/b\.py$/.test(loc.uri), 'def should be in b.py');
				assert.equal(loc.range.start.line, 0, `def should be on line 0`);
				assert.equal(loc.range.start.character, 6, `def should be on char 6`);
			});
	});
});
