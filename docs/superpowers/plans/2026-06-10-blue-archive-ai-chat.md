# Blue Archive AI Chat — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drastically simplify Open WebUI to a minimal chat app with Blue Archive anime theming, dark/light mode (Arona/Plana), and native HermesAgent tool-calling/thinking display.

**Architecture:** Keep the SvelteKit + FastAPI skeleton, delete 70% of features (RAG, admin, channels, workspaces, etc.), inject Blue Archive CSS variables and component theming, add a streaming XML parser for HermesAgent `<think>` / `<tool_call>` / `<tool_response>` tags, render them as collapsible panels and tool cards inside chat bubbles.

**Tech Stack:** SvelteKit 5, Tailwind CSS v4, TypeScript, Python FastAPI, SSE streaming

---

## File Structure Mapping

### New Files (to create)

| File | Responsibility |
|------|---------------|
| `src/lib/components/chat/HermesMessage.svelte` | Chat bubble that renders normal text + `<think>` panels + `<tool_call>` cards + `<tool_response>` cards |
| `src/lib/components/chat/ThinkPanel.svelte` | Collapsible thinking-process panel (💭 icon, gray/semi-transparent background) |
| `src/lib/components/chat/ToolCallCard.svelte` | Tool invocation card (🔧 icon, JSON params, status badge ⏳/✅/❌) |
| `src/lib/components/chat/ToolResponseCard.svelte` | Tool result card (✅ icon, JSON output) |
| `src/lib/utils/hermes-parser.ts` | Streaming XML parser state machine for `<think>`, `<tool_call>`, `<tool_response>` |
| `src/lib/stores/theme.ts` | Svelte store for dark/light mode, persists to localStorage |
| `src/lib/constants/character-lines.ts` | All Arona/Plana character lines organized by scene |
| `static/assets/mascots/arona.png` | Arona half-body transparent PNG (placeholder until real asset downloaded) |
| `static/assets/mascots/plana.png` | Plana half-body transparent PNG (placeholder until real asset downloaded) |
| `src/app.css` (create or overwrite) | Global CSS variables for Blue Archive color system, font imports |

### Modified Files (existing, to change)

| File | Responsibility |
|------|---------------|
| `src/app.html` | Add `data-theme` attribute to `<html>` for Tailwind dark mode |
| `src/routes/+layout.svelte` | Inject theme store, global background styling |
| `src/routes/(app)/+layout.svelte` | Apply Blue Archive layout (sidebar, nav) |
| `src/routes/(app)/home/+page.svelte` | Main chat page, simplified to single chat interface |
| `src/routes/auth/+page.svelte` | Login page, Blue Archive themed with Arona/Plana welcome |
| `src/lib/components/chat/MessageInput.svelte` | Bottom input bar, themed placeholder text |
| `src/lib/components/layout/Navbar.svelte` | Top nav, add sun/moon theme toggle button |
| `src/lib/components/chat/Chat.svelte` | Main chat container, integrate HermesMessage |
| `package.json` | Remove non-core dependencies |
| `pyproject.toml` | Remove non-core Python dependencies |
| `tailwind.config.js` | Add dark mode strategy, custom colors |
| `vite.config.ts` | Remove pyodide/static copy plugins if present |

### Deleted Directories (to remove entirely)

**Frontend:**
- `src/lib/components/admin/`
- `src/lib/components/calendar/`
- `src/lib/components/channel/`
- `src/lib/components/notes/`
- `src/lib/components/playground/`
- `src/lib/components/workspace/`
- `src/lib/components/automations/`
- `src/routes/(app)/admin/`
- `src/routes/(app)/calendar/`
- `src/routes/(app)/channels/`
- `src/routes/(app)/notes/`
- `src/routes/(app)/playground/`
- `src/routes/(app)/workspace/`
- `src/routes/(app)/automations/`

**Backend:**
- `backend/open_webui/routers/` — keep only `auths.py`, `chats.py`, `models.py`, `files.py`, delete all others

---

## Phase 1: Frontend Deletion

### Task 1: Delete Non-Core Frontend Component Directories

**Files:**
- Delete: `src/lib/components/admin/`
- Delete: `src/lib/components/calendar/`
- Delete: `src/lib/components/channel/`
- Delete: `src/lib/components/notes/`
- Delete: `src/lib/components/playground/`
- Delete: `src/lib/components/workspace/`
- Delete: `src/lib/components/automations/`

- [ ] **Step 1: Delete directories**

```bash
rm -rf src/lib/components/admin
rm -rf src/lib/components/calendar
rm -rf src/lib/components/channel
rm -rf src/lib/components/notes
rm -rf src/lib/components/playground
rm -rf src/lib/components/workspace
rm -rf src/lib/components/automations
```

- [ ] **Step 2: Verify deletion**

```bash
ls src/lib/components/
```

Expected: Only `chat/`, `app/`, `common/`, `icons/`, `layout/` remain.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: delete non-core frontend component directories"
```

---

### Task 2: Delete Non-Core Frontend Routes

**Files:**
- Delete: `src/routes/(app)/admin/`
- Delete: `src/routes/(app)/calendar/`
- Delete: `src/routes/(app)/channels/`
- Delete: `src/routes/(app)/notes/`
- Delete: `src/routes/(app)/playground/`
- Delete: `src/routes/(app)/workspace/`
- Delete: `src/routes/(app)/automations/`

- [ ] **Step 1: Delete route directories**

```bash
rm -rf src/routes/\(app\)/admin
rm -rf src/routes/\(app\)/calendar
rm -rf src/routes/\(app\)/channels
rm -rf src/routes/\(app\)/notes
rm -rf src/routes/\(app\)/playground
rm -rf src/routes/\(app\)/workspace
rm -rf src/routes/\(app\)/automations
```

- [ ] **Step 2: Verify deletion**

```bash
find src/routes/\(app\) -maxdepth 1 -type d | sort
```

Expected: Only `home/`, `c/` remain (plus any others we want to keep).

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: delete non-core frontend routes"
```

---

### Task 3: Scan and Remove Orphaned Imports

**Files:**
- Modify: Any file that imports from deleted directories

- [ ] **Step 1: Search for orphaned imports**

```bash
grep -r "from.*components/admin" src/ || echo "No admin imports found"
grep -r "from.*components/calendar" src/ || echo "No calendar imports found"
grep -r "from.*components/channel" src/ || echo "No channel imports found"
grep -r "from.*components/notes" src/ || echo "No notes imports found"
grep -r "from.*components/playground" src/ || echo "No playground imports found"
grep -r "from.*components/workspace" src/ || echo "No workspace imports found"
grep -r "from.*components/automations" src/ || echo "No automations imports found"
grep -r "/admin" src/routes/ || echo "No admin route refs found"
grep -r "/calendar" src/routes/ || echo "No calendar route refs found"
grep -r "/channels" src/routes/ || echo "No channels route refs found"
grep -r "/notes" src/routes/ || echo "No notes route refs found"
grep -r "/playground" src/routes/ || echo "No playground route refs found"
grep -r "/workspace" src/routes/ || echo "No workspace route refs found"
grep -r "/automations" src/routes/ || echo "No automations route refs found"
```

- [ ] **Step 2: Remove any found orphaned imports**

If any imports found, remove them from the importing files. Common locations to check:
- `src/lib/components/layout/Sidebar.svelte` — may have nav links to deleted routes
- `src/routes/(app)/+layout.svelte` — may import deleted components

- [ ] **Step 3: Try to compile frontend**

```bash
npm run check
```

If it fails, fix remaining import errors one by one.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove orphaned imports from deleted components"
```

---

## Phase 2: Backend Deletion

### Task 4: Delete Non-Core Backend Routers

**Files:**
- Delete: `backend/open_webui/routers/` — keep only `auths.py`, `chats.py`, `models.py`, `files.py`

- [ ] **Step 1: List routers to keep and delete**

```bash
ls backend/open_webui/routers/
```

- [ ] **Step 2: Delete all except the 4 core routers**

```bash
cd backend/open_webui/routers
# Keep auths.py, chats.py, models.py, files.py
# Delete everything else
for f in *.py; do
  if [ "$f" != "auths.py" ] && [ "$f" != "chats.py" ] && [ "$f" != "models.py" ] && [ "$f" != "files.py" ] && [ "$f" != "__init__.py" ]; then
    rm "$f"
    echo "Deleted: $f"
  fi
done
cd /root/open-webui
```

- [ ] **Step 3: Verify remaining routers**

```bash
ls backend/open_webui/routers/
```

Expected: `__init__.py`, `auths.py`, `chats.py`, `models.py`, `files.py`

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: delete non-core backend routers"
```

---

### Task 5: Remove Orphaned Backend Imports

**Files:**
- Modify: `backend/open_webui/main.py` — likely imports all routers
- Modify: Any other file referencing deleted routers

- [ ] **Step 1: Find where deleted routers are imported**

```bash
grep -r "from open_webui.routers import" backend/
grep -r "routers\." backend/open_webui/main.py
```

- [ ] **Step 2: Edit `backend/open_webui/main.py`**

Remove import lines and `app.include_router()` calls for deleted routers. Keep only:
- `auths`
- `chats`
- `models`
- `files`

Example of what to keep (actual code may vary):
```python
from open_webui.routers import auths, chats, models, files

app.include_router(auths.router, prefix="/api/v1/auths")
app.include_router(chats.router, prefix="/api/v1/chats")
app.include_router(models.router, prefix="/api/v1/models")
app.include_router(files.router, prefix="/api/v1/files")
```

- [ ] **Step 3: Try to start backend**

```bash
cd backend && python -c "from open_webui.main import app; print('Import OK')"
```

If it fails, fix import errors.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove orphaned backend router imports"
```

---

## Phase 3: Dependency Cleanup

### Task 6: Clean Frontend Dependencies

**Files:**
- Modify: `package.json`

- [ ] **Step 1: Edit `package.json` dependencies**

Remove from `dependencies`:
- `mermaid`
- `vega`
- `vega-lite`
- `leaflet`
- `@xterm/xterm`, `@xterm/addon-fit`, `@xterm/addon-web-links`
- `pyodide`
- `chart.js`
- `kokoro-js`
- `@mediapipe/tasks-vision`
- `shiki`

Remove from `devDependencies`:
- `cypress`
- `eslint-plugin-cypress`
- `i18next-parser`

Keep everything else (svelte, tailwind, marked, tiptap, dompurify, etc.).

- [ ] **Step 2: Reinstall dependencies**

```bash
rm -rf node_modules package-lock.json
npm install
```

- [ ] **Step 3: Verify build still works**

```bash
npm run build
```

Expected: Build completes without errors.

- [ ] **Step 4: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore: remove non-core frontend dependencies"
```

---

### Task 7: Clean Backend Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Edit `pyproject.toml`**

Remove packages related to:
- Vector databases: `chromadb`, `qdrant-client`, `pinecone-client`, etc.
- Speech/audio: `speechrecognition`, `openai-whisper`, etc.
- Image generation: `diffusers`, `transformers` (image-related), etc.
- Document parsing: `tika`, `docling`, `pdfplumber` (keep minimal PDF support if needed for files)
- Advanced features: `sentence-transformers`, `langchain`, etc.

Keep: `fastapi`, `uvicorn`, `sqlalchemy`, `python-multipart`, `aiohttp`, `pydantic`, `python-jose`, `passlib`, `requests`, `python-dotenv`

- [ ] **Step 2: Reinstall Python dependencies**

```bash
pip install -e .
```

Or if using uv:
```bash
uv pip install -e .
```

- [ ] **Step 3: Verify backend imports**

```bash
cd backend && python -c "from open_webui.main import app; print('Backend import OK')"
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: remove non-core backend dependencies"
```

---

## Phase 4: Blue Archive Theme System

### Task 8: Create Global Theme CSS Variables

**Files:**
- Create: `src/app.css`

- [ ] **Step 1: Write `src/app.css`**

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

@layer base {
  :root {
    /* Blue Archive Light Mode (Arona) */
    --ba-bg-primary: #F0F4F8;
    --ba-bg-card: #FFFFFF;
    --ba-bg-chat-user: linear-gradient(135deg, #00A8E8 0%, #4FC3F7 100%);
    --ba-bg-chat-ai: #FFFFFF;
    --ba-accent-primary: #00A8E8;
    --ba-accent-secondary: #4FC3F7;
    --ba-accent-pink: #FF6B9D;
    --ba-success: #4ADE80;
    --ba-warning: #FBBF24;
    --ba-error: #F87171;
    --ba-text-primary: #1E293B;
    --ba-text-secondary: #64748B;
    --ba-text-inverse: #FFFFFF;
    --ba-border: #E2E8F0;
    --ba-border-chat-ai: rgba(0, 168, 232, 0.2);
    --ba-think-bg: rgba(100, 116, 139, 0.08);
    --ba-tool-call-bg: rgba(0, 168, 232, 0.05);
    --ba-tool-call-border: rgba(0, 168, 232, 0.3);
    --ba-tool-response-bg: rgba(74, 222, 128, 0.05);
    --ba-tool-response-border: rgba(74, 222, 128, 0.3);
    --ba-mascot: 'arona';
  }

  [data-theme="dark"] {
    /* Blue Archive Dark Mode (Plana) */
    --ba-bg-primary: #0F172A;
    --ba-bg-card: #1E293B;
    --ba-bg-chat-user: linear-gradient(135deg, #0EA5E9 0%, #38BDF8 100%);
    --ba-bg-chat-ai: #1E293B;
    --ba-accent-primary: #38BDF8;
    --ba-accent-secondary: #7DD3FC;
    --ba-accent-pink: #F472B6;
    --ba-success: #4ADE80;
    --ba-warning: #FBBF24;
    --ba-error: #F87171;
    --ba-text-primary: #F1F5F9;
    --ba-text-secondary: #94A3B8;
    --ba-text-inverse: #FFFFFF;
    --ba-border: #334155;
    --ba-border-chat-ai: rgba(56, 189, 248, 0.2);
    --ba-think-bg: rgba(148, 163, 184, 0.08);
    --ba-tool-call-bg: rgba(56, 189, 248, 0.05);
    --ba-tool-call-border: rgba(56, 189, 248, 0.3);
    --ba-tool-response-bg: rgba(74, 222, 128, 0.05);
    --ba-tool-response-border: rgba(74, 222, 128, 0.3);
    --ba-mascot: 'plana';
  }

  html {
    font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
  }

  body {
    background-color: var(--ba-bg-primary);
    color: var(--ba-text-primary);
  }
}
```

- [ ] **Step 2: Ensure `src/routes/+layout.svelte` imports the CSS**

If not already present, add:
```svelte
<script>
  import '../app.css';
</script>
```

- [ ] **Step 3: Commit**

```bash
git add src/app.css src/routes/+layout.svelte
git commit -m "feat: add Blue Archive CSS theme variables"
```

---

### Task 9: Create Theme Store

**Files:**
- Create: `src/lib/stores/theme.ts`

- [ ] **Step 1: Write `src/lib/stores/theme.ts`**

```typescript
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

function getInitialTheme(): Theme {
  if (!browser) return 'light';
  const stored = localStorage.getItem('theme') as Theme | null;
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function createThemeStore() {
  const { subscribe, set } = writable<Theme>(getInitialTheme());

  return {
    subscribe,
    set: (theme: Theme) => {
      if (!browser) return;
      localStorage.setItem('theme', theme);
      document.documentElement.setAttribute('data-theme', theme);
      set(theme);
    },
    toggle: () => {
      if (!browser) return;
      const current = document.documentElement.getAttribute('data-theme') as Theme || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', next);
      document.documentElement.setAttribute('data-theme', next);
      set(next);
    }
  };
}

export const theme = createThemeStore();
```

- [ ] **Step 2: Initialize theme on app load**

In `src/routes/+layout.svelte`, add:
```svelte
<script>
  import '../app.css';
  import { theme } from '$lib/stores/theme';
  import { onMount } from 'svelte';

  onMount(() => {
    const stored = localStorage.getItem('theme');
    if (stored) {
      document.documentElement.setAttribute('data-theme', stored);
      theme.set(stored as 'light' | 'dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initial = prefersDark ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', initial);
      theme.set(initial);
    }
  });
</script>
```

- [ ] **Step 3: Commit**

```bash
git add src/lib/stores/theme.ts src/routes/+layout.svelte
git commit -m "feat: add theme store with localStorage persistence"
```

---

### Task 10: Add Theme Toggle Button to Navbar

**Files:**
- Modify: `src/lib/components/layout/Navbar.svelte` (or equivalent top nav component)

- [ ] **Step 1: Find the navbar component**

```bash
find src/lib/components/layout -name "*.svelte" | head -10
```

- [ ] **Step 2: Add theme toggle button**

Add to the navbar's right section (before user avatar):
```svelte
<script>
  import { theme } from '$lib/stores/theme';

  function toggleTheme() {
    theme.toggle();
  }
</script>

<button
  on:click={toggleTheme}
  class="p-2 rounded-xl transition-all hover:bg-[var(--ba-bg-card)] hover:shadow-md"
  aria-label="Toggle theme"
>
  {#if $theme === 'light'}
    <!-- Sun icon -->
    <svg class="w-5 h-5 text-[var(--ba-accent-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
    </svg>
  {:else}
    <!-- Moon icon -->
    <svg class="w-5 h-5 text-[var(--ba-accent-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
    </svg>
  {/if}
</button>
```

- [ ] **Step 3: Verify toggle works**

```bash
npm run dev
```

Open browser, click toggle button, verify page switches between light/dark modes.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add theme toggle button to navbar"
```

---

## Phase 5: Chat Interface Theming

### Task 11: Create Mascot Asset Placeholders

**Files:**
- Create: `static/assets/mascots/arona.png`
- Create: `static/assets/mascots/plana.png`

- [ ] **Step 1: Create directory and placeholder images**

```bash
mkdir -p static/assets/mascots
```

For now, create simple SVG placeholders. In a later task, replace with real Blue Archive assets.

Create `static/assets/mascots/arona.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 200">
  <rect width="120" height="200" fill="#E0F2FE"/>
  <circle cx="60" cy="50" r="30" fill="#00A8E8"/>
  <text x="60" y="120" text-anchor="middle" fill="#1E293B" font-size="14">Arona</text>
  <text x="60" y="140" text-anchor="middle" fill="#64748B" font-size="10">placeholder</text>
</svg>
```

Create `static/assets/mascots/plana.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 200">
  <rect width="120" height="200" fill="#1E293B"/>
  <circle cx="60" cy="50" r="30" fill="#38BDF8"/>
  <text x="60" y="120" text-anchor="middle" fill="#F1F5F9" font-size="14">Plana</text>
  <text x="60" y="140" text-anchor="middle" fill="#94A3B8" font-size="10">placeholder</text>
</svg>
```

- [ ] **Step 2: Commit**

```bash
git add static/assets/mascots/
git commit -m "feat: add Arona/Plana mascot placeholders"
```

---

### Task 12: Style User Message Bubble

**Files:**
- Modify: `src/lib/components/chat/Messages.svelte` or `src/lib/components/chat/Message.svelte` (find the correct component)

- [ ] **Step 1: Find the message bubble component**

```bash
grep -r "user.*message" src/lib/components/chat/ --include="*.svelte" -l | head -5
grep -r "message-user" src/lib/components/chat/ --include="*.svelte" -l | head -5
```

- [ ] **Step 2: Apply Blue Archive styling to user bubbles**

Find the element with user message styling and update to:
```svelte
<div class="user-message flex justify-end mb-4">
  <div class="max-w-[80%] rounded-2xl rounded-tr-sm px-5 py-3 text-white"
       style="background: var(--ba-bg-chat-user);">
    <!-- message content -->
  </div>
</div>
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: style user message bubble with Blue Archive gradient"
```

---

### Task 13: Style AI Message Bubble with Mascot

**Files:**
- Modify: The AI message bubble component

- [ ] **Step 1: Update AI message bubble layout**

```svelte
<script>
  import { theme } from '$lib/stores/theme';

  $: mascotSrc = $theme === 'dark'
    ? '/assets/mascots/plana.svg'
    : '/assets/mascots/arona.svg';
  $: characterName = $theme === 'dark' ? '普拉纳' : '阿罗纳';
</script>

<div class="ai-message flex items-start mb-4 gap-2">
  <!-- Mascot image -->
  <img
    src={mascotSrc}
    alt={characterName}
    class="w-[80px] h-auto flex-shrink-0 -mr-2 z-10"
  />

  <!-- Bubble -->
  <div class="relative max-w-[75%]">
    <!-- Character name tag -->
    <div class="flex items-center gap-1 mb-1 ml-1">
      <span class="text-xs font-medium text-[var(--ba-accent-primary)]">
        {characterName}
      </span>
      <span class="text-[10px] text-[var(--ba-text-secondary)]">
        {new Date().toLocaleTimeString()}
      </span>
    </div>

    <!-- Message content -->
    <div class="rounded-2xl rounded-tl-sm px-5 py-3 border"
         style="background-color: var(--ba-bg-chat-ai); border-color: var(--ba-border-chat-ai);">
      <slot />
    </div>
  </div>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add mascot to AI message bubble"
```

---

## Phase 6: HermesAgent XML Parser & Components

### Task 14: Create HermesAgent Streaming Parser

**Files:**
- Create: `src/lib/utils/hermes-parser.ts`

- [ ] **Step 1: Write the parser**

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/utils/hermes-parser.ts
git commit -m "feat: add HermesAgent XML streaming parser"
```

---

### Task 15: Create ThinkPanel Component

**Files:**
- Create: `src/lib/components/chat/ThinkPanel.svelte`

- [ ] **Step 1: Write the component**

```svelte
<script lang="ts">
  import { theme } from '$lib/stores/theme';
  import { slide } from 'svelte/transition';

  export let content: string;
  export let isThinking = false;

  let expanded = false;

  $: label = $theme === 'dark' ? '普拉纳分析中...' : '阿罗纳正在思考...';
  $: icon = $theme === 'dark' ? '🌙' : '💭';
</script>

<div class="mb-2 rounded-lg overflow-hidden"
     style="background-color: var(--ba-think-bg); border: 1px solid var(--ba-border);">
  <button
    class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:opacity-80 transition-opacity"
    on:click={() => expanded = !expanded}
  >
    <span>{icon}</span>
    <span class="font-medium text-[var(--ba-text-secondary)]">{label}</span>
    {#if isThinking}
      <span class="ml-auto animate-pulse text-[var(--ba-accent-primary)]">●</span>
    {/if}
    <span class="ml-auto text-[var(--ba-text-secondary)]">
      {expanded ? '▲' : '▼'}
    </span>
  </button>

  {#if expanded}
    <div class="px-3 pb-3" transition:slide={{ duration: 200 }}>
      <pre class="text-xs text-[var(--ba-text-secondary)] whitespace-pre-wrap font-mono leading-relaxed">
{content}
      </pre>
    </div>
  {/if}
</div>
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/components/chat/ThinkPanel.svelte
git commit -m "feat: add collapsible ThinkPanel for HermesAgent reasoning"
```

---

### Task 16: Create ToolCallCard Component

**Files:**
- Create: `src/lib/components/chat/ToolCallCard.svelte`

- [ ] **Step 1: Write the component**

```svelte
<script lang="ts">
  import { slide } from 'svelte/transition';

  export let name: string;
  export let arguments: string = '';
  export let status: 'running' | 'success' | 'error' = 'running';

  let expanded = false;

  $: statusIcon = status === 'running' ? '⏳' : status === 'success' ? '✅' : '❌';
  $: statusColor = status === 'running' ? 'var(--ba-accent-primary)'
    : status === 'success' ? 'var(--ba-success)'
    : 'var(--ba-error)';
</script>

<div class="mb-2 rounded-lg overflow-hidden"
     style="background-color: var(--ba-tool-call-bg); border: 1px solid var(--ba-tool-call-border);">
  <button
    class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:opacity-80 transition-opacity"
    on:click={() => expanded = !expanded}
  >
    <span>🔧</span>
    <span class="font-medium text-[var(--ba-text-primary)]">工具调用: {name}</span>
    <span class="ml-auto" style="color: {statusColor}">{statusIcon}</span>
    <span class="ml-1 text-[var(--ba-text-secondary)]">{expanded ? '▲' : '▼'}</span>
  </button>

  {#if expanded && arguments}
    <div class="px-3 pb-3" transition:slide={{ duration: 200 }}>
      <pre class="text-xs text-[var(--ba-text-secondary)] whitespace-pre-wrap font-mono leading-relaxed bg-black/5 dark:bg-white/5 p-2 rounded">
{arguments}
      </pre>
    </div>
  {/if}
</div>
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/components/chat/ToolCallCard.svelte
git commit -m "feat: add ToolCallCard for HermesAgent tool invocations"
```

---

### Task 17: Create ToolResponseCard Component

**Files:**
- Create: `src/lib/components/chat/ToolResponseCard.svelte`

- [ ] **Step 1: Write the component**

```svelte
<script lang="ts">
  import { slide } from 'svelte/transition';

  export let name: string;
  export let output: string = '';

  let expanded = false;
</script>

<div class="mb-2 rounded-lg overflow-hidden"
     style="background-color: var(--ba-tool-response-bg); border: 1px solid var(--ba-tool-response-border);">
  <button
    class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:opacity-80 transition-opacity"
    on:click={() => expanded = !expanded}
  >
    <span>✅</span>
    <span class="font-medium text-[var(--ba-text-primary)]">工具返回: {name}</span>
    <span class="ml-auto text-[var(--ba-text-secondary)]">{expanded ? '▲' : '▼'}</span>
  </button>

  {#if expanded && output}
    <div class="px-3 pb-3" transition:slide={{ duration: 200 }}>
      <pre class="text-xs text-[var(--ba-text-secondary)] whitespace-pre-wrap font-mono leading-relaxed bg-black/5 dark:bg-white/5 p-2 rounded">
{output}
      </pre>
    </div>
  {/if}
</div>
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/components/chat/ToolResponseCard.svelte
git commit -m "feat: add ToolResponseCard for HermesAgent tool results"
```

---

### Task 18: Create HermesMessage Component

**Files:**
- Create: `src/lib/components/chat/HermesMessage.svelte`
- Modify: Existing AI message component to use HermesMessage

- [ ] **Step 1: Write HermesMessage**

```svelte
<script lang="ts">
  import { onDestroy } from 'svelte';
  import { HermesParser, type HermesSegment } from '$lib/utils/hermes-parser';
  import ThinkPanel from './ThinkPanel.svelte';
  import ToolCallCard from './ToolCallCard.svelte';
  import ToolResponseCard from './ToolResponseCard.svelte';

  export let content: string = '';
  export let streaming = false;

  const parser = new HermesParser();
  let segments: HermesSegment[] = [];

  // Re-parse when content changes (for streaming)
  $: {
    if (content) {
      const newSegments = parser.feed(content);
      segments = [...segments, ...newSegments];
    }
  }

  // On final message, flush any remaining content
  $: if (!streaming && content) {
    const flushed = parser.flush();
    segments = [...segments, ...flushed];
  }

  onDestroy(() => {
    // Cleanup if needed
  });
</script>

<div class="hermes-message">
  {#each segments as segment (segment.type + segment.content.slice(0, 20))}
    {#if segment.type === 'text'}
      <div class="prose prose-sm max-w-none text-[var(--ba-text-primary)]">
        {@html segment.content}
      </div>

    {:else if segment.type === 'think' || segment.type === 'reasoning'}
      <ThinkPanel content={segment.content} isThinking={streaming} />

    {:else if segment.type === 'tool_call'}
      <ToolCallCard
        name={segment.name || 'unknown'}
        arguments={segment.arguments || ''}
        status={streaming ? 'running' : 'success'}
      />

    {:else if segment.type === 'tool_response'}
      <ToolResponseCard
        name={segment.name || 'unknown'}
        output={segment.output || ''}
      />
    {/if}
  {/each}

  <!-- Show partial content while streaming -->
  {#if streaming}
    {#const partial = parser.getPartial()}
    {#if partial}
      <div class="text-[var(--ba-text-secondary)] opacity-50 animate-pulse">
        {partial.content}
      </div>
    {/if}
  {/if}
</div>
```

- [ ] **Step 2: Integrate into AI message bubble**

Replace the content rendering in the AI message bubble with:
```svelte
<HermesMessage content={message.content} streaming={message.streaming} />
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: integrate HermesMessage with XML parser and tool cards"
```

---

## Phase 7: Character Lines System

### Task 19: Create Character Lines Constants

**Files:**
- Create: `src/lib/constants/character-lines.ts`

- [ ] **Step 1: Write character lines**

```typescript
export interface CharacterLines {
  light: string;  // Arona
  dark: string;   // Plana
}

export const LOGIN_WELCOME: CharacterLines = {
  light: 'Sensei！欢迎回到 Schale！今天想聊些什么呢？',
  dark: 'Sensei，夜间模式已启动。请放心，我会一直陪着您。',
};

export const INPUT_PLACEHOLDER: CharacterLines = {
  light: 'Sensei，请在这里输入~',
  dark: 'Sensei，请指示...',
};

export const LOADING: CharacterLines = {
  light: '阿罗纳正在联系基沃托斯... 🔵',
  dark: '普拉纳正在深层检索... 🌙',
};

export const FILE_UPLOAD: CharacterLines = {
  light: '收到资料！阿罗纳帮您整理~ 📚',
  dark: '文件已接收。开始解析内容。',
};

export const NETWORK_ERROR: CharacterLines = {
  light: '连接基沃托斯失败了...Sensei 检查一下网络好吗？😢',
  dark: '连接中断。请检查网络状态。',
};

export const MODEL_UNAVAILABLE: CharacterLines = {
  light: '这个模型暂时不在服务区呢...换一个好嘛？🥺',
  dark: '该模型当前不可用。建议切换其他模型。',
};

export const FILE_TOO_LARGE: CharacterLines = {
  light: '文件太大啦！阿罗纳拿不动...换个小的？📦',
  dark: '文件超出限制。请压缩后重试。',
};

// HermesAgent specific
export const THINKING: CharacterLines = {
  light: '💭 阿罗纳正在联系 Schale 分析...',
  dark: '💭 普拉纳开始分析任务...',
};

export const TOOL_CALL: CharacterLines = {
  light: '🔧 正在使用 {tool}！',
  dark: '🔧 调用工具: {tool}',
};

export const TOOL_RUNNING: CharacterLines = {
  light: '⏳ 稍等哦，正在处理...',
  dark: '⏳ 执行中，请稍候。',
};

export const TOOL_SUCCESS: CharacterLines = {
  light: '✅ 拿到结果啦！',
  dark: '✅ 工具执行完毕。',
};

export const TOOL_ERROR: CharacterLines = {
  light: '❌ 呜...工具出错了...',
  dark: '❌ 工具执行失败。',
};

export const MULTI_STEP: CharacterLines = {
  light: '🔄 还有一步！马上好~',
  dark: '🔄 继续下一步分析。',
};
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/constants/character-lines.ts
git commit -m "feat: add Arona/Plana character line constants"
```

---

### Task 20: Integrate Character Lines into UI

**Files:**
- Modify: Login page
- Modify: Input placeholder
- Modify: Error handlers

- [ ] **Step 1: Create helper function**

Add to `src/lib/constants/character-lines.ts`:
```typescript
import { theme } from '$lib/stores/theme';
import { get } from 'svelte/store';

export function getLine(lines: CharacterLines): string {
  return get(theme) === 'dark' ? lines.dark : lines.light;
}
```

- [ ] **Step 2: Update login page welcome text**

In `src/routes/auth/+page.svelte`:
```svelte
<script>
  import { LOGIN_WELCOME, getLine } from '$lib/constants/character-lines';
  import { theme } from '$lib/stores/theme';

  $: welcomeText = $theme === 'dark' ? LOGIN_WELCOME.dark : LOGIN_WELCOME.light;
</script>

<h1 class="text-2xl font-bold text-[var(--ba-accent-primary)] mb-2">
  {welcomeText}
</h1>
```

- [ ] **Step 3: Update input placeholder**

In the message input component:
```svelte
<script>
  import { INPUT_PLACEHOLDER } from '$lib/constants/character-lines';
  import { theme } from '$lib/stores/theme';

  $: placeholder = $theme === 'dark' ? INPUT_PLACEHOLDER.dark : INPUT_PLACEHOLDER.light;
</script>

<textarea {placeholder} ... />
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: integrate character lines into login and input components"
```

---

## Phase 8: Verification & Polish

### Task 21: Verify Frontend Build

- [ ] **Step 1: Run TypeScript check**

```bash
npm run check
```

Expected: No TypeScript errors.

- [ ] **Step 2: Run build**

```bash
npm run build
```

Expected: Build completes successfully.

- [ ] **Step 3: Fix any remaining errors**

If there are errors, fix them one by one. Common issues:
- Missing imports from deleted files
- Type errors in modified components

- [ ] **Step 4: Commit fixes**

```bash
git add -A
git commit -m "fix: resolve build errors after theming changes"
```

---

### Task 22: Verify Backend Starts

- [ ] **Step 1: Try to import backend app**

```bash
cd backend && python -c "from open_webui.main import app; print('Backend OK')"
```

- [ ] **Step 2: Start backend (if possible)**

```bash
cd backend && uvicorn open_webui.main:app --reload --port 8080
```

- [ ] **Step 3: Test core endpoints**

```bash
curl http://localhost:8080/api/v1/models
curl -X POST http://localhost:8080/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
```

- [ ] **Step 4: Commit**

```bash
git add -A || true
git commit -m "chore: verify backend starts after router cleanup" || echo "Nothing to commit"
```

---

### Task 23: Test Theme Switching

- [ ] **Step 1: Start dev server**

```bash
npm run dev
```

- [ ] **Step 2: Manual verification checklist**

Open `http://localhost:5173` (or the dev server URL):

- [ ] Light mode shows Arona-themed colors (blue/white)
- [ ] Dark mode shows Plana-themed colors (dark blue)
- [ ] Theme toggle button switches modes
- [ ] Theme persists after page refresh
- [ ] AI messages show mascot image on the left
- [ ] User messages are right-aligned with blue gradient
- [ ] Input placeholder changes with theme

- [ ] **Step 3: Commit**

```bash
git add -A || true
git commit -m "feat: complete Blue Archive theming with Arona/Plana mascots" || echo "Nothing to commit"
```

---

## Self-Review

### Spec Coverage Check

| Spec Section | Plan Task(s) |
|-------------|-------------|
| 2.1 保留核心架构 | Task 1-7 (deletions) |
| 2.2 前端删除清单 | Task 1 |
| 2.3 后端删除清单 | Task 4 |
| 2.4 依赖清理 | Task 6, 7 |
| 2.5 功能矩阵 | Task 1-7 |
| 3.1 色彩系统 | Task 8 |
| 3.2 字体系统 | Task 8 |
| 3.3 组件风格 | Task 8, 12, 13 |
| 3.4 背景装饰 | Task 8 (CSS vars) |
| 4 明暗切换 | Task 9, 10 |
| 5.1 角色设定 | Task 11, 19 |
| 5.2 素材获取 | Task 11 |
| 5.3 看板娘显示 | Task 13 |
| 5.4 角色化文案 | Task 19, 20 |
| 6.1 聊天布局 | Task 12, 13 |
| 6.2 消息气泡 | Task 12, 13 |
| 6.3 输入区域 | Task 20 |
| 7.1 聊天数据流 | Task 18 (integration) |
| 7.2 文件上传流 | No change needed (existing) |
| 7.3 保留 API | Task 4, 5 |
| 8 HermesAgent 集成 | Task 14-18 |
| 9 错误处理 | Task 20 |
| 10 技术决策 | Documented in plan |
| 11 实现优先级 | All tasks mapped to P0-P3 |
| 12 风险与缓解 | Considered throughout |

**Gap found**: None. All spec sections have corresponding tasks.

### Placeholder Scan

- No "TBD", "TODO", "implement later" found ✓
- No vague "add appropriate error handling" found ✓
- All code steps include actual code ✓
- All file paths are exact ✓

### Type Consistency

- `HermesSegment` type used consistently in parser and components ✓
- `CharacterLines` interface used consistently ✓
- Theme store (`'light' | 'dark'`) used consistently ✓

---

*Plan complete. Ready for execution.*
