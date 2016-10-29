import { TextDocument } from "vscode-languageserver";



export enum Flags {
	Local = 1 << 0,
	Filesystem = 1 << 1,
	Overlay = 1 << 2,
}

export interface SourceSnapshot {
	flags: Flags;
	content: string;
	version: number;
	getContent(): string;
	getPath(): string;
	getFullText(): string;
}
