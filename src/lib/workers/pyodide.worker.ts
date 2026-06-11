// Pyodide worker is not available
self.onmessage = (event) => {
	const { id } = event.data;
	self.postMessage({
		id,
		stderr: 'Pyodide is not available',
		stdout: '',
		result: null
	});
};

export default {};
