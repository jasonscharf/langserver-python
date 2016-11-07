

import * as mocha from 'mocha';
import * as assert from 'assert';
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

import { TextDocumentPositionParams, TextDocumentIdentifier } from 'vscode-languageclient';
import { Hover } from 'vscode-languageserver';

import { exec } from '../utils/exec';
import { Marker, getMarkers } from '../utils/markers';


suite('hover', () => {
	const root = vscode.workspace.rootPath;
	const dataPath = "../../src/test/data";
	const filePath = 'hover.py'
	const uri = vscode.Uri.file(path.join(root, dataPath, filePath));

	test('test hover.py', () => {
		const testHover = (marker: Marker, result: any, ix) => {
			let length: number = 0;
			let content: string = null;

			// Handle promiselike 
			if (typeof result === 'object') {
				length = result.length;
				if (length > 0) {
					content = result[0].contents[0]['value'];
				}
			}
			else if (typeof result === "array") {
				var res = <any>result;
				length = res.length;
				content = res[0]['value'];
			}

			const pre = `${marker.msg}`;

			assert.ok(length > 0, `${pre} but found no results`);
			assert.equal(content, marker.expected, `${pre} but got '${content}'`);
		};

		const handleHoverResults = (results: Hover[], markers) => {
			assert.ok(results != null && Array.isArray(results), 'should get an array of results');
			assert.ok(results.length > 0, 'should have at least one hover result');
			return markers
				.map((marker, ix) => testHover(marker, results[ix], ix));
		};

		const markers = getMarkers(fs.readFileSync(uri.fsPath).toString());
		const promises =
			markers.map((marker, ix) => exec("vscode.executeHoverProvider", uri, marker.start));

		return Promise.all(promises)
			.then(results => handleHoverResults(results, markers))
	});
});
