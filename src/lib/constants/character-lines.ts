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

import { theme } from '$lib/stores/theme';
import { get } from 'svelte/store';

export function getLine(lines: CharacterLines): string {
  return get(theme) === 'dark' ? lines.dark : lines.light;
}
