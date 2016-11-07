import * as mocha from 'mocha';
import * as assert from 'assert';
import * as path from 'path';
import * as vscode from 'vscode';
import { Location } from 'vscode-languageclient';
import { SymbolInformation } from 'vscode-languageserver';
import * as globals from '../../../src/globals';
import { exec } from '../utils/exec';


export function symbols(query: string): Thenable<SymbolInformation[]> {
	return exec("vscode.executeWorkspaceSymbolProvider", null, query);
}

suite('symbols', () => {
	const commonAssert = (symbols: SymbolInformation[]) => {
		assert.ok(symbols, 'received response from workspace/symbol');
		assert.ok(symbols.length > 0, 'expected at least one symbol');
		return symbols;
	};

	test('found', () => {
		return symbols('SymbolA')
			.then(commonAssert)
			.then(symbols => {
				assert.equal(symbols.length, 1, 'should find 1 symbol for SymbolA');
				assert.equal(symbols[0].name, 'SymbolA', 'should find SymbolA and not some other symbol');
			});
	});

	test('found in nested workspace folders', () => {
		return symbols('SymbolC')
			.then(commonAssert)
			.then(symbols => {
				assert.equal(symbols.length, 1, 'should find SymbolC, which is nested in a submodule folder');
				assert.equal(symbols[0].name, 'SymbolC', 'should find SymbolC');
			});
	});

	test('found in various workspace files', () => {
		return symbols('common_method_with_4_instances')
			.then(commonAssert)
			.then(symbols => {
				assert.ok(symbols.length === 4, 'should find common_method_with_4_instances in multiple locations');
				symbols
					.map(sym => sym.name)
					.filter(name => assert.equal(symbols[0].name, 'common_method_with_4_instances', 'should only find symbol common_method_with_4_instances'))
					;
				
			});
	});
});
