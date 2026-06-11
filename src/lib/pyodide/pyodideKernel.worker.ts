// Pyodide kernel worker is not available
self.onmessage = (event) => {
	const { type, id } = event.data;
	if (type === 'execute') {
		self.postMessage({
			type: 'result',
			id,
			state: {
				id,
				status: 'error',
				result: null,
				stdout: '',
				stderr: 'Pyodide is not available'
			}
		});
	} else {
		self.postMessage({ type: 'initialized' });
	}
};
