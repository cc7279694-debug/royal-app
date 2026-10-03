# Clash Tracker

本项目从用户主动提供的本地 MP4 开始，研究离线画面分析。
目前只有 **Module 1 离线录像读取工具**：读取视频信息、按时间导出完整 PNG、
生成 JSON 报告。它在 Windows 电脑上运行，不需要 Android Studio。

实时在线对局分析和 HUD 保持 Gated：须取得覆盖具体行为、版本、使用场景的
Supercell 官方明确许可。用户接受风险、只读屏幕、本地运行、小号或训练场均不能
代替许可；即使获得许可，也不承诺绝不封号。

## Windows PowerShell 操作

在 PowerShell 中按顺序执行。已安装并验证 Python 3.12.4；后续 Android 技术栈
不由这个实验工具决定。无需激活虚拟环境，也无需修改执行策略。

### 1. 进入项目、检查 Python、安装工具

```powershell
Set-Location "E:\CODEX\royal app"
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple --only-binary=:all: -r tools/offline_video/requirements-test.txt
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps -e tools/offline_video
```

本次环境已安装好，通常只需进入项目。上述命令适用于重新安装；依赖版本全部固定。
首次安装依赖需要联网，工具运行不需要联网。若 wheel 不可用，安装会明确失败，
不会自动编译 FFmpeg/PyAV。请保留错误输出，不要改用全局安装。

### 2. 放入录像

```powershell
New-Item -ItemType Directory -Force "local_data\recordings" | Out-Null
```

把自己的一段 MP4 放到 `local_data\recordings\sample.mp4`。
建议 30–60 秒、正常速度的对局回放、完整竖屏画面。
`local_data/`、`outputs/` 和虚拟环境已被 Git 忽略，录像和截图不会提交到 GitHub。

### 3. 查看信息

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video inspect "local_data\recordings\sample.mp4"
```

显示文件名、首个实际视频流索引（排除封面图）、编码、原始宽高、
元数据时长及来源、平均 FPS、显示旋转和警告。
缺失时长/FPS显示 unknown；平均 FPS 不用于抽帧计算。
inspect 只验证首个解码帧，并不保证整段视频没有损坏。

### 4. 导出画面与报告

以下是真正可用的 PowerShell 单行命令。时间是录像首个显示帧之后的秒数，
不是游戏内倒计时。每次使用新目录：

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video extract "local_data\recordings\sample.mp4" --times 0 1.5 10 --output ("outputs\module1\run-" + [guid]::NewGuid().ToString("N"))
```

每项选择时间戳不早于目标的第一帧，允许晚 **最多 100ms，含边界**。
超出容差或最后显示帧之后的请求会标为 miss，不用最后一帧冒充结果。
相邻时间可能命中同一帧，报告会保留相同原始 PTS，分别输出 PNG。

输出目录包含 `frame_0000.png` 等成功图片和 `report.json`。
报告保存请求时间、实际时间、误差、原始 PTS/time_base、归一化时间、图片名、
原始尺寸、输出尺寸、旋转和每项状态。不包含输入文件的完整私人路径。
打开 `outputs\module1` 下本次运行目录查看 PNG 和报告：

```powershell
Invoke-Item "outputs\module1"
```

退出码：0 = 所有时间命中；3 = 至少一项未命中（已有报告）；2 = 参数、解码、
时间轴或文件错误。输出目录必须不存在或为空，输入与已有文件绝不自动覆盖/清空。
发生错误时可能保留部分 PNG 和 error 报告，请用新目录重试。

### 5. 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q
```

测试在临时目录编码合成视频，验证实际解码、PTS选帧、旋转、PNG内容、错误与
文件保护。只提交素材生成代码，不提交视频和抽帧输出。

## 当前支持范围

- 常规本地 MP4，Windows x64 + Python 3.12，已验证合成 H.264 8-bit SDR；
  支持能力取决于安装包中的解码器，不承诺所有 MP4 编码。
- 使用实际 PTS/time_base，顺序扫描到结束，一次保留一帧；
  没有随机寻址优化，长视频处理耗时随长度增长。
- 0/90/180/270 度纯旋转；不裁切、不缩放、不改变完整画面的比例。
- 明确拒绝非直角旋转、镜像/缩放/透视显示矩阵、非方形像素、已标记 HDR、
  高于 8-bit 的帧及异常时间轴。未标记的色彩信息不能据此认证为 SDR。
- 仅解码所选视频流；不分析音频，不上传文件，不连接账号、设备或运行中的游戏。
- 合成素材与用户提供的 H.264 竖屏录像均已验证，Module 1 已完成。
  已验证录像为 448 × 960、约 273.17 秒、约 30 FPS；不代表所有手机格式均适配。

## 项目事实源

- [项目定义](PROJECT.md)
- [当前状态](docs/CURRENT_STATE.md)
- [决策](docs/DECISIONS.md)
- [开发计划](docs/DEVELOPMENT_PLAN.md)
- [Module 1 验证与依赖来源](docs/VERIFICATION_M1.md)
- [协作约束](AGENTS.md)
