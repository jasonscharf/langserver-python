
// TODO: Review or reconcile (replace) with proper JSON-RPC or VS code typings
export interface JediMessage<T> {
	id?: number;
	result: T;
}

export interface JediResponse<T> extends JediMessage<T> {
	result: T;
}

export interface JediRequest<T> extends JediMessage<T> {
	id?: number;
}

export interface Ping extends JediMessage<number> {
	result: number;
}

export interface Pong extends Ping {
	result: number;
}
