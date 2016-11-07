import * as vscode from 'vscode';

const DEFAULT_MARKER = "#";


export interface Marker {
	raw: string;
	start: vscode.Position;
	expected: string;
	msg: string;
}

// Pulls simple text markers from a test case file for the purposes of annotating expected test results.
export function getMarkers(content: string) {
	const lines = content.split('\n');
	const markers = lines
		.map((raw, line) => {
			const preamble = raw.indexOf(DEFAULT_MARKER);
			if (preamble < 0) {
				return null;
			}
			else {
				line = line + 1;
				const meta = raw.slice(preamble + DEFAULT_MARKER.length).trim();
				const char = raw.slice(0, preamble).replace(/\t/g, '    ').length;
				const start = new vscode.Position(line, char);
				const pieces = meta.split('|');

				let msg = meta.trim();
				let expected: string = null;

				if (pieces.length > 1) {
					let piece = pieces[1].trim();
					if (/^expect\s+/.test(piece)) {
						expected = piece.replace(/^expect\s+/, '').trim();
						msg = `Expected '${expected}' at [${line},${char}]`;
					}
				}

				return <Marker>{
					raw,
					start,
					expected,
					msg,
				};
			}
		})
		.filter(marker => !!marker);

	return markers;
}
