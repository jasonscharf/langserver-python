export namespace event {
	let _readyCb;
	let _readyPromise;

	export function ready() {
		if (_readyCb) {
			_readyCb();
		}
	}

	export function onReady() {
		if (_readyPromise) {
			return _readyPromise;
		}
		else {
			return _readyPromise = new Promise((resolve, reject) => {
				_readyCb = () => {
					resolve();
				}
			});
		}
	}
}
