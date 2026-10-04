# Clash Tracker

本项目从用户主动提供的本地 MP4 开始，研究离线画面分析。
现有 **Module 1 离线录像读取工具**，以及 **Module 2A1 证据准备工具**：
读取视频、导出完整 PNG、准备索引和联系表、校验人工证据并报告数据不足。
Module 2A1 已于 2026-10-04 正式验收，验收基准为
`98037ceba81683ad1a2c214bada30a10f2f3f69e`；并不代表可以开始训练模型。
工具在 Windows 电脑上运行，不需要 Android Studio，不会自动识别卡牌。

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

## Module 2A1：本地人工证据

使用现有环境，无需安装新依赖。三个命令独立于 Module 1：

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video.evidence_cli prepare "local_data\recordings\sample.mp4" --recording-id recording_01 --output "outputs\evidence\new-survey"
.\.venv\Scripts\python.exe -m clash_tracker_video.evidence_cli validate "outputs\evidence\evidence.json" --indexes "outputs\evidence\new-survey\index.json"
.\.venv\Scripts\python.exe -m clash_tracker_video.evidence_cli review "outputs\evidence\evidence.json" --indexes "outputs\evidence\new-survey\index.json" --output "outputs\evidence\new-review.json"
```

输出目录或报告必须全新，不能重复使用；只能放在项目 `outputs/` 或
`local_data/`。禁止 URL、网络路径、路径穿越、符号链接及 junction。
正常命令输出不显示私人路径。所有截图、索引、标注及详细报告仅保留本地。

prepare 默认每五秒采样并加入真实最后一帧，精确去重；可用
`--times 0 0.1 0.2` 指定更细的定位时间。输出 `exports/` 原始 PNG、
Module 1 `report.json`、`index.json` 和 `contacts/` 预览。
联系表只用于定位，标框必须依据旋转校正后的完整原始 PNG。

**prepare 不会生成已确认的部署证据。** 人工观看完整录像后，按
[证据契约](docs/superpowers/specs/2026-10-03-module-2a-evidence-preparation-design.md)
建立六实体 JSON：recordings、match_segments、target_card、occurrences、
frame_annotations、negative_intervals；writer 使用 schema_version=1。
每次 verified 部署需要缺席→新出现→持续可见的依据、已确认归属/视角/变体、
3～5 个不同真实时间戳的关键框。无法确认保持 ambiguous/draft，未知区间
不能当负样本。同一帧的重复导出不会增加关键证据数量。

可在本地 Python 中使用 `evidence_review.normalize_box` 和
`make_frame_annotation` 辅助坐标录入；不会自动升级 draft。
多个抽帧运行可通过 `--indexes INDEX1 INDEX2` 合并，真实帧身份稳定，
重复帧尺寸、时间戳或图像内容冲突会报错。人工视角写入 evidence；
prepare 索引中的 unknown 不会自动推断为某一方。

普通区间右端不包含；仅到达实际最后一帧的终止负样本可包含右端。
区间未完成会报告 coverage_gaps，不要求逐帧标框。

退出码：prepare 成功 0、部分命中 3、错误 2；validate 有效 0、错误 2；
review 有效但不足 3、无效/错误 2。review 在 2A1 永远
`experiment_gate=false`，候选门槛是独立结论；没有 freeze 命令。

当前真实录像由用户完成整局观看；执行者核对原始抽帧，记录四次对手普通
地狱飞龙部署及 12 张关键帧框。候选门槛通过，但仍有八个明确报告的未知区间，
并未完成全时间轴负样本认证。单场录像的训练门槛保持关闭，review 正确返回
insufficient。这是已验收的人工证据，不是模型识别结果；未知区间不能当负样本。
2A1 已完成验收记录及快进整合；`main` 基线为 `3ad657f…`，原功能分支保留。
用户于 2026-10-04 另行正式授权 Module 2A2 实施。2B、Module 3、Android 和
实时 HUD 仍未批准或开始；2A1 review 仍不代表新实验就绪。
参见 [Module 2A1 验证记录](docs/VERIFICATION_M2A1.md)。

## Module 2A2：独立证据与实验锁

本模块已授权，开发就绪与不可覆盖冻结基础设施已实现，不修改上述三条命令，
不训练或运行模型。现已收到四份录像，用户确认来自四场新的、完整、正常速度且
未剪辑的自然对局回放。仅第一份暂选为开发候选并准备了 37 张定位画面，其余
三份未查看、未分配。整局人工复核、选卡和开发冻结尚未完成，不能宣称
`DEV_LOCKED` 或 Module 2A2 完成；文件检查不能代替这些人工确认。

新增独立实验命令：`readiness`、`freeze-development`、`validate-lock`、
`freeze-test-gt`。最后一条仅提供未来盲测契约，当前未开展真实测试／模型工作。
基础设施阶段最新完整测试 385 项通过、1 项权限跳过，依赖检查和本地打包通过；
本次录像接收未改代码，未重跑该测试集。复核记录见下方验证文档。
命令细节见数据契约，无需你手动编写标注 JSON。

第一轮改为：一场**新的自然开发对局**，人工整局复核后从对手实际用过的卡中选
一个明确形态，至少两次清晰独立部署；没有合格目标就换下一场自然对局，不降低
标准。旧地狱飞龙录像只用于历史回归，不能默认沿用为第一张模型目标。
普通、觉醒和未知形态分开；未知区间及另一形态不能作为负样本。

开发数据锁定后仍须独立验收及 2B 授权。后续顺序为：开发锁 → 模型锁 → 独立
测试录像及新会话人工标注 → 测试标注锁 → 首次整场模型推理；不得先看预测再改
标签。同一真实比赛即使重录或换文件，也不能跨开发/测试。

### 下一份录像怎么准备

正常打一场游戏，结束后从**对战记录打开完整回放**，用系统录屏从开头录到结算，
正常速度，不剪辑、不倍速、不安排对手。无需提前挑卡。
推荐放到 `local_data\recordings\development_01.mp4`（该目录已创建并被忽略）。
已提供的录像保留原文件名，无需改名或重复准备；实际映射保存在忽略的本地清单。

以下是新输入的准备命令示例，用于定位画面，不是训练或自动认牌：

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video.evidence_cli prepare "local_data\recordings\development_01.mp4" --recording-id development_01 --output ("outputs\module2a2\dev-survey-" + [guid]::NewGuid().ToString("N"))
```

现有 prepare 的参数和退出码已核对。每次新目录；不会覆盖录像或先前输出。
缺少录像时不执行这条命令。后续人工证据和新实验冻结使用不同的流程，不能用
contact 缩略图或模型预测替代整局人工复核。

参见 [盲测协议](docs/MODULE_2A2_BLIND_TEST_PROTOCOL.md)、
[数据契约](docs/MODULE_2A2_CONTRACTS.md)、
[本轮验证记录](docs/VERIFICATION_M2A2.md)。

## 项目事实源

- [项目定义](PROJECT.md)
- [当前状态](docs/CURRENT_STATE.md)
- [决策](docs/DECISIONS.md)
- [开发计划](docs/DEVELOPMENT_PLAN.md)
- [Module 1 验证与依赖来源](docs/VERIFICATION_M1.md)
- [协作约束](AGENTS.md)
