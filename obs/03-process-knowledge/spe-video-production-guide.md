# SPE 快速入门视频 — 制作执行方案（Production SOP）

> **执行者**：Content Ops 团队 - video_producer / ai_visual_creator
> **对应分镜脚本**：`obs/03-process-knowledge/spe-video-script-mvp.md`
> **视频时长**：约 4 分钟
> **形式**：屏幕录制 + AI 旁白（剪映 TTS）
> **工具栈**：OBS Studio + 剪映桌面版（全免费）
>
> **⚠️ 注意**：本文档是早期"人工录屏"方案，已被 HTML Cinema Pipeline 取代。
> 保留作历史参考，实际生产请使用 `video-production-pipeline-knowledge.md` 中描述的自动化 Pipeline。

---

## Part 1：制作前准备清单

### 1.1 工具安装与配置

#### OBS Studio 安装

1. 打开浏览器，访问 https://obsproject.com/download
2. 点击 **Windows** 下载按钮，下载安装程序
3. 运行安装程序，全部选默认选项，点"下一步"直到安装完成
4. 首次启动 OBS 时，弹出"自动配置向导"，选择 **"我只使用录制功能"**，点击"下一步"完成向导

**OBS 录制设置（必须手动配置）**：

打开 OBS → 菜单栏 → 文件 → 设置，按以下逐项配置：

**视频 选项卡**：
| 设置项 | 值 | 说明 |
|--------|------|------|
| 基础（画布）分辨率 | 1920x1080 | 录制画面大小 |
| 输出（缩放）分辨率 | 1920x1080 | 保持与画布一致，不缩放 |
| 常用帧率值 | 30 | 教程视频 30fps 足够，文件更小 |

**输出 选项卡**（选择"高级"模式）：
| 设置项 | 值 | 说明 |
|--------|------|------|
| 录制格式 | MKV | 录制时用 MKV 防崩溃丢失，后续转 MP4 |
| 编码器 | 如有 NVIDIA 显卡选 `NVENC H.264`；否则选 `x264` | 硬件编码更快 |
| 码率控制 | CRF | 恒定质量模式 |
| CRF 值 | 18 | 数字越小画质越高，18 是高画质平衡点 |
| 关键帧间隔 | 2 | 秒 |

**音频 选项卡**：
| 设置项 | 值 | 说明 |
|--------|------|------|
| 采样率 | 44.1 kHz | 标准 |
| 声道 | 立体声 | 标准 |

> **重要**：视频不录制麦克风音频（旁白后期用 TTS 合成），将 OBS 中"桌面音频"和"麦克风"全部**静音**，确保录制素材无杂音。

#### 剪映桌面版安装

1. 访问 https://www.capcut.cn/（中国大陆）或 https://www.capcut.com/（海外）
2. 点击"免费下载"，下载桌面版安装包
3. 运行安装程序，按默认选项安装，注册/登录免费账户

#### 终端环境准备

确保以下已安装：
1. **Windows Terminal**：Windows 11 自带
2. **JetBrains Mono 字体**：从 https://www.jetbrains.com/mono/ 下载，全选 .ttf 文件右键安装
3. **Starship prompt**（可选）：`winget install --id Starship.Starship`

---

### 1.2 终端美化方案

**目标效果**：黑色终端背景（#0f172a），JetBrains Mono 字体，青色光标，与 SPE 使用手册配色一致。

Windows Terminal settings.json 关键配置：
```json
{
  "profiles": {
    "defaults": {
      "font": { "face": "JetBrains Mono", "size": 16 },
      "colorScheme": "One Half Dark",
      "background": "#0f172a",
      "cursorShape": "bar",
      "cursorColor": "#14b8a6"
    }
  }
}
```

---

## Part 2：逐场景录制指南

### 场景概览

| 场景 | 时长 | 内容 |
|------|------|------|
| 场景 1 | 00:00-00:30 | Hook — 痛点共鸣 |
| 场景 2 | 00:30-01:15 | /capture 演示 |
| 场景 3 | 01:15-02:15 | /plan-day 演示 |
| 场景 4 | 02:15-03:00 | /time-block 演示 |
| 场景 5 | 03:00-03:35 | /weekly-review 演示 |
| 场景 6 | 03:35-04:00 | 总结 + CTA |

### 录制流程

每个场景的标准流程：
1. 准备终端内容（预制输出文本，不依赖实际 API）
2. Alt+F9 开始录制
3. 按分镜脚本逐步演示
4. Alt+F9 停止录制
5. 命名保存：`scene-{N}-take-{X}.mkv`

---

## Part 3：TTS 旁白生成

**工具**：剪映桌面版内置 TTS（无需 API Key）

**推荐声音**：云希（男声，专业感强）或云扬（男声，清晰）

**流程**：
1. 剪映 → 文本 → 智能文稿 → 粘贴旁白文本
2. 选择声音 → 生成音频
3. 导出 MP3 文件

---

## Part 4：剪辑合成

**项目设置**：1920x1080，30fps，时间线按场景顺序排列

**合成流程**：
1. 导入所有场景素材（MKV）
2. 导入 TTS 音频
3. 对齐音视频时间线
4. 添加场景转场（推荐：滑动过渡）
5. 添加侧边信息图（G1-G6，PNG/SVG 素材）
6. 颜色调整：饱和度微增，亮度对比标准
7. 导出：MP4，H.264，码率 8Mbps

---

## Part 5：质量检查清单

- [ ] 分辨率 1920x1080 ✓
- [ ] 总时长 3:40-4:20 之间 ✓
- [ ] 无杂音/麦克风噪音 ✓
- [ ] TTS 旁白与画面对齐（误差 ≤ 0.5s）✓
- [ ] 所有侧边信息图清晰可读 ✓
- [ ] 文件大小 < 50MB ✓
- [ ] 在 Windows + macOS 浏览器中播放正常 ✓

---

## 附：为什么此方案已被取代

本方案要求人类手动操作 OBS 录屏，AI Agent 团队无法自动执行。

2026-04-12 团队转向 **HTML Cinema Pipeline**：
- HTML/CSS/JS 动画模拟终端界面
- Playwright headless 录制（零人工）
- Edge TTS 配音（零人工）
- FFmpeg 合成（零人工）
- 结果：100% 代码驱动，2:41 分钟 MVP 成片

详见：`obs/03-process-knowledge/video-production-pipeline-knowledge.md`
