export interface HermesSegment {
  type: 'text' | 'think' | 'tool_call' | 'tool_response';
  content: string;
  // For tool_call/tool_response
  name?: string;
  arguments?: string;
  output?: string;
}

export class HermesParser {
  private buffer = '';
  private segments: HermesSegment[] = [];
  private currentSegment: HermesSegment | null = null;
  private state: 'text' | 'in_think' | 'in_tool_call' | 'in_tool_response' = 'text';

  private tagStack: string[] = [];

  feed(chunk: string): HermesSegment[] {
    this.buffer += chunk;
    const completed: HermesSegment[] = [];

    while (this.buffer.length > 0) {
      const result = this.processBuffer();
      if (result) {
        completed.push(result);
      } else {
        break;
      }
    }

    return completed;
  }

  private processBuffer(): HermesSegment | null {
    if (this.state === 'text') {
      const thinkStart = this.buffer.indexOf('<think>');
      const reasoningStart = this.buffer.indexOf('<reasoning>');
      const toolCallStart = this.buffer.indexOf('<tool_call>');
      const toolResponseStart = this.buffer.indexOf('<tool_response>');

      const tags = [
        { pos: thinkStart, tag: 'think', endTag: '</think>' },
        { pos: reasoningStart, tag: 'reasoning', endTag: '</reasoning>' },
        { pos: toolCallStart, tag: 'tool_call', endTag: '</tool_call>' },
        { pos: toolResponseStart, tag: 'tool_response', endTag: '</tool_response>' },
      ].filter(t => t.pos !== -1);

      if (tags.length === 0) {
        // No tags found, flush all as text
        const text = this.buffer;
        this.buffer = '';
        return text ? { type: 'text', content: text } : null;
      }

      // Find earliest tag
      tags.sort((a, b) => a.pos - b.pos);
      const earliest = tags[0];

      // Flush text before tag
      if (earliest.pos > 0) {
        const text = this.buffer.substring(0, earliest.pos);
        this.buffer = this.buffer.substring(earliest.pos);
        return { type: 'text', content: text };
      }

      // Enter tag mode
      this.state = earliest.tag as 'think' | 'in_tool_call' | 'in_tool_response';
      if (this.state === 'think') this.state = 'in_think';

      // Remove opening tag
      const openTagLen = earliest.tag.length + 2; // <tag>
      this.buffer = this.buffer.substring(openTagLen);
      this.currentSegment = { type: earliest.tag as 'think' | 'tool_call' | 'tool_response', content: '' };
      return null;
    }

    // In tag mode, look for closing tag
    const endTag = this.state === 'in_think' ? '</think>'
      : this.state === 'in_tool_call' ? '</tool_call>'
      : '</tool_response>';

    const endPos = this.buffer.indexOf(endTag);

    if (endPos === -1) {
      // Closing tag not yet received
      // Keep buffering, but yield partial content for streaming display
      return null;
    }

    // Found closing tag
    const content = this.buffer.substring(0, endPos);
    this.buffer = this.buffer.substring(endPos + endTag.length);

    const segment = this.currentSegment!;
    segment.content = content;

    // Parse tool-specific fields
    if (segment.type === 'tool_call') {
      const nameMatch = content.match(/<name>(.*?)<\/name>/s);
      const argsMatch = content.match(/<arguments>(.*?)<\/arguments>/s);
      if (nameMatch) segment.name = nameMatch[1].trim();
      if (argsMatch) segment.arguments = argsMatch[1].trim();
    } else if (segment.type === 'tool_response') {
      const nameMatch = content.match(/<name>(.*?)<\/name>/s);
      const outputMatch = content.match(/<output>(.*?)<\/output>/s);
      if (nameMatch) segment.name = nameMatch[1].trim();
      if (outputMatch) segment.output = outputMatch[1].trim();
    }

    this.state = 'text';
    this.currentSegment = null;
    return segment;
  }

  // Get current partial content for streaming display
  getPartial(): HermesSegment | null {
    if (this.state === 'text') return null;
    return {
      type: this.currentSegment?.type || 'text',
      content: this.buffer
    };
  }

  flush(): HermesSegment[] {
    const remaining: HermesSegment[] = [];
    if (this.buffer.length > 0) {
      remaining.push({
        type: this.state === 'text' ? 'text' : (this.currentSegment?.type || 'text'),
        content: this.buffer
      });
    }
    this.buffer = '';
    this.state = 'text';
    this.currentSegment = null;
    return remaining;
  }
}
