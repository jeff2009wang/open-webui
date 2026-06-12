# Blue Archive 二次元主题素材集成设计

## 目标

将 Blue Archive（蔚蓝档案）官方风格的 MomoTalk 头像、角色立绘等二次元素材完整应用到 Open WebUI 前端，实现自动化下载、分类存储、主题绑定和前端渲染。

## 数据源

**主数据源：SchaleDB**
- API: `https://schaledb.com/data/cn/students.json`
- 图片 CDN: `https://schaledb.com/images/student/<type>/<Id>.webp`
- 三种图片类型：
  - `icon/<Id>.webp` — 角色头像（~10KB）
  - `portrait/<Id>.webp` — 全身立绘（~120KB）
  - `collection/<Id>.webp` — 收集背景（~18KB）

**补充来源：Blue Archive Wiki / Fandom**
- CG 画廊、剧情插图
- 手动下载高稀有度 CG

## 角色分配

| 主题 | 角色 | SchaleDB ID | 用途 |
|------|------|-------------|------|
| Light | 白子 (Shiroko) | 10010 | 头像、登录页背景、侧边栏 |
| Dark | 星野 (Hoshino) | 10005 | 头像、登录页背景、侧边栏 |
| 通用-加载 | 爱丽丝 (Aris) | 10015 | 加载页、空状态 |
| 通用-欢迎 | 未花 (Mika) | 10059 | 欢迎页、特殊场景 |

## 文件存储结构

```
static/assets/ba/
├── students/
│   ├── icon/
│   │   ├── 10005.webp
│   │   ├── 10010.webp
│   │   ├── 10015.webp
│   │   └── 10059.webp
│   ├── portrait/
│   │   ├── 10005.webp
│   │   ├── 10010.webp
│   │   ├── 10015.webp
│   │   └── 10059.webp
│   └── index.json        # 角色ID → 名字 → 路径映射
├── cg/                   # 剧情CG（Wiki来源）
│   └── ...
└── mascots/
    ├── arona.svg         # 现有SVG占位图
    └── plana.svg
```

## 自动化脚本

**脚本：`scripts/download-ba-assets.py`**

功能：
1. 从 SchaleDB API 拉取角色列表
2. 按角色 ID 批量下载三类图片
3. 保存到 `static/assets/ba/students/` 对应目录
4. 生成 `index.json` 索引文件
5. 支持增量更新（只下载新角色或缺失文件）
6. 支持 `--characters` 参数指定角色 ID

```bash
# 下载指定角色
python scripts/download-ba-assets.py --characters 10005,10010,10015,10059

# 下载全部角色
python scripts/download-ba-assets.py --all
```

## 前端应用位置

### 1. 登录页 (`auth/+page.svelte`)

- **背景**：当前主题对应的角色 portrait 立绘作为全屏背景
- **蒙版**：半透明渐变遮罩（确保文字可读性）
- **角色台词**：浮动在输入框上方，使用 `character-lines.ts` 中已有台词
- **Light/Dark 切换**：切换主题时背景立绘淡入淡出

### 2. 侧边栏 (`Sidebar.svelte`)

- **顶部区域**：显示当前主题角色的圆形头像 icon
- **主题切换**：点击切换时头像平滑过渡（淡入淡出）
- **头像下方**：显示角色名 + 学校名

### 3. 聊天界面 (`ResponseMessage.svelte`)

- **AI 头像**：每条 AI 消息左侧显示角色 icon 头像
- **Hermes 解析器**：`think` 面板和 `tool_call` 卡片旁显示角色 icon
- **头像切换**：Light 主题用白子，Dark 主题用星野

### 4. 加载与空状态

- **加载页**：爱丽丝立绘 + 角色台词动画
- **网络错误**：星野头像 + "连接基沃托斯失败了" 提示
- **空聊天**：未花头像 + 引导语

### 5. 主题切换动画

- 切换主题时：
  - 背景立绘淡入淡出
  - 头像切换带 200ms 过渡
  - CSS 主题变量同步更新

## 技术实现

### 图片加载优化

- 使用 `<img loading="lazy" decoding="async">`
- 静态资源走 Vite 构建缓存
- 图片 404 时回退到现有 SVG placeholder

### 主题绑定

- `theme.ts` store 中增加 `mascotId` 字段
- `getMascotForTheme(theme: Theme): { icon: string, portrait: string, name: string }`
- 主题切换时自动更新 mascot

### 回退机制

- 素材缺失时：显示 SVG placeholder + 角色名文字
- API 不可用：跳过下载，使用已有素材
- 图片加载失败：CSS `background-color` 兜底

## 前端风格规范（蔚蓝档案风格）

- **圆角**：大量使用 `rounded-2xl` / `rounded-3xl`
- **色彩**：使用 CSS 变量 `--ba-*`，保持 light/dark 一致性
- **字体**：日文/中文混合排版，支持角色台词的日文原名
- **动效**：淡入淡出、轻微弹跳（角色台词出现时的动画）
- **布局**：卡片式布局，留白充足，避免信息拥挤

## 测试验证

1. 脚本执行后检查 `static/assets/ba/` 目录结构
2. 前端页面验证：登录页、侧边栏、聊天界面均显示正确角色
3. 主题切换验证：Light/Dark 切换时角色和背景同步变化
4. 回退验证：删除素材文件后页面不崩溃，显示 placeholder

## 自动化测试（ITUT）

### 接口测试（Interface Test）

**测试目标**：素材下载脚本和后端 API 的可靠性

**测试项**：
1. `download-ba-assets.py` 脚本：
   - SchaleDB API 可访问性（HTTP 200）
   - 图片下载完整性（文件大小 > 0）
   - `index.json` 生成正确性（ID→路径映射完整）
   - 增量更新逻辑（重复运行不重复下载）
   - 断网回退（API 不可用时跳过，不崩溃）

2. 后端模型 API：
   - `/api/models` 返回 pipe model（TestEchoPipe 存在）
   - `/api/v1/models` 返回空数组或正确数据
   - 删除的路由返回 404 且不阻塞前端

### UI 测试（UI Test）

**测试目标**：前端主题素材正确渲染

**测试项**：
1. 登录页：
   - Light 主题显示白子立绘背景
   - Dark 主题显示星野立绘背景
   - 背景图加载成功（非 placeholder）

2. 侧边栏：
   - 当前主题角色头像正确显示
   - 主题切换时头像平滑过渡

3. 聊天界面：
   - AI 消息旁显示角色头像
   - HermesMessage 解析器工作正常

4. 主题切换：
   - Light → Dark 切换时背景图变化
   - 所有角色素材对应正确主题

**测试工具**：Playwright 自动化脚本（复用现有 `test_webapp_full.py`）
