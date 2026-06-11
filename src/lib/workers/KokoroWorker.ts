export class KokoroWorker {
	constructor(_dtype: string = 'fp32') {}

	public async init() {
		throw new Error('Kokoro TTS is not available');
	}

	public async generate(_params: { text: string; voice: string }): Promise<string> {
		throw new Error('Kokoro TTS is not available');
	}

	public terminate() {}
}
