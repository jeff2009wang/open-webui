// Kokoro worker is not available
self.onmessage = async (event) => {
	const { type } = event.data;
	if (type === 'init') {
		self.postMessage({ status: 'init:error', error: 'Kokoro TTS is not available' });
	} else if (type === 'generate') {
		self.postMessage({ status: 'generate:error', error: 'Kokoro TTS is not available' });
	} else {
		self.postMessage({ status: 'status:check', initialized: false });
	}
};
