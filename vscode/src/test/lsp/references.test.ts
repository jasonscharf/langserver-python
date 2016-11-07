import * as mocha from 'mocha';
import * as assert from 'assert';
import * as path from 'path';
import * as vscode from 'vscode';
import { Location } from 'vscode-languageclient';

import { exec } from '../utils/exec';

const root = vscode.workspace.rootPath;
const dataPath = "../../src/test/data";
const filePath = 'definitions.py'


export function references(filename: string, line: number, char: number): Thenable<Location[]> {
	const pos = new vscode.Position(line, char);
	const uri = vscode.Uri.file(path.join(root, dataPath, filename));
	return exec("vscode.executeReferenceProvider", uri, pos);
}

suite('references', () => {
	const commonAssert = (refs: Location[]) => {
		assert.ok(refs, 'received response from textDocument/references');
		assert.ok(refs.length > 0, 'expected at least one reference result');
		return refs;
	};

	test('resolved in same folder', () => {
		return references('references/qualified-imports.py', 4, 15)
			.then(commonAssert)
			.then(refs => {
				assert.ok(refs.length > 0, `multiple references should be found`);
			});
	});

	test('resolved in subfolder bearing __init__.py', () => {
		return references('references/qualified-imports.py', 5, 17)
			.then(commonAssert)
			.then(refs => {
				const first = refs[0];
				assert.ok(/b\.py$/.test(first.uri.toString()), 'def should be in b.py');
				assert.equal(first.range.start.line, 0, `def should be on line 0`);
				assert.equal(first.range.start.character, 6, `def should be on char 6`);
			});
	});

	test('resolved for bound import symbol RefDefA', () => {
		return references('references/bound.py', 0, 20)
			.then(commonAssert)
			.then(refs => {
				assert.equal(refs.length, 8, 'should be 7 refs to RefDefA');
			});
	});

	test('resolved for bound import symbols from qualified imports', () => {
		return references('references/bound.py', 1, 30)
			.then(commonAssert)
			.then(refs => {
				assert.equal(refs.length, 4, 'should be 3 refs to SubmoduleDefA');
			});
	});

	test('resolved for aliased import symbols', () => {
		return references('references/aliased.py', 0, 31)
			.then(commonAssert)
			.then(refs => {
				assert.equal(refs.length, 8, 'should be 8 refs to the underlying symbol of alias AAA');
			});
	});

	test('resolved for aliased import symbols from qualified imports', () => {
		return references('references/aliased.py', 1, 36)
			.then(commonAssert)
			.then(refs => {
				// Note: Unused import in __init.py__ doesn't count
				assert.equal(refs.length, 4, 'should be 4 refs to the underlying symbol of alias AAA');
			});
	});

	test('do not yield false positives on non-unique symbols', () => {
		return references('definitions.py', 4, 10)
			.then(commonAssert)
			.then(refs => {
				assert.equal(refs.length, 1, 'should only be 1 reference to symbol common_method_with_4_instances');
				assert.ok(refs[0].uri.toString().indexOf("definitions.py") > 0, 'the only file bearing reference should be definitions.py');
			});
	});
});
