# Clash Tracker

**当前：Milestone 2 第二批审核包已准备；实体 Android 手机测试等待用户。**
严格续接首批结束位置：第一场 72–129.5 秒，每 2.5 秒一帧，24 张原图、
491 个待审候选、4 张 contact sheets。48 个原始 teacher labels 含 UI／噪声，
不是确认类别；本批新增 confirmed GT=0。ChatGPT 建议仍须用户明确确认后才能回填。
本次只对这 24 帧生成新 proposals；旧 benchmark、首批 GT、旧实验与模型环境不变，
没有训练或自动 Negative。一次 NMS 超时警告及原日志已保留，不调参重跑。
审核 ZIP 在私有忽略目录 `outputs/milestone2/second-gt-and-real-device/`，
原图可能含玩家 UI，仅供用户控制的私人审核交接，不是公开素材或法律 clearance。
当前设备查询仅有模拟器，没有真实手机；`REAL_DEVICE_TEST_PENDING_USER`。
现有 APK 不重建、不改功能；安装命令、手动安装和触屏／真正冷启动清单在同目录
`b2/INSTALL_AND_CHECKLIST.md`。真机安装、启动、2/8、Reset 与布局均未冒充通过。
不训练、不进入 Module 3／真实游戏 HUD，不 push／合并 main。
见[本阶段实际证据](docs/VERIFICATION_MILESTONE2.md)。

**已完成的前序 checkpoint：首个模拟 App Debug APK；用户确认的首批视觉 GT。**
模拟功能不变，不接真实游戏、不训练。APK 声明最低 Android 7.0 / API24；
模拟器启动、模拟 2/8、Reset 已验证，实体手机安装尚未验证。
首批 526 个候选中，44 框接受、2 项拒绝、480 项仍 pending/unknown；确认 6 个
visual classes、5 个非空 canonical mappings。reviewer=user，依据为 ChatGPT
视觉审核建议，不把 ChatGPT 写成人类审核者。本批 0 Negative、0 confirmed card plays，
不训练。新 annotation-only GT snapshot/lock 不覆盖旧锁，仍 training_qualified=false。
见[Milestone 2 验证](docs/VERIFICATION_MILESTONE2.md)。

**已实现并验证：本地预标注／人工纠错工具 + 纯模拟 App 原型。**
KataCR 只提供待审核候选，不直接成为人工 GT 或最终 App 识别核心。
支持接受／拒绝／改类／改框／补框及逐类穷尽复核；Unknown、拒绝与未标区域
不自动成为 Negative。严格按原录像顺序，第二场中途截断，仍不具备训练资格。
10–20 类只是目标；当前不训练、不改旧锁或实验结果。
React + TypeScript + Capacitor 原型只用女巫／气球兵模拟事件展示已发现 2/8；
HUD 只在 App 内，不接游戏、detector、实时录屏或跨应用悬浮窗。
不实现卡序／觉醒／圣水；真实游戏 HUD 保持关闭。
见[当前两任务设计与边界](docs/superpowers/specs/2026-10-07-preannotation-and-simulated-app-design.md)。

Milestone 1 的原始预标注页面仍保留 12 张原图和 272 个待审候选，未被修改；
五种纠错操作与独立回传导入已用合成演示实际走通。
见[预标注操作](tools/preannotation/README.md)和[模拟 App 操作](app/README.md)。
模拟 App 已通过测试、Web 构建、Capacitor Android 同步和 Debug 编译。
本轮 JDK / SDK 使用项目内独立忽略目录，没有改全局环境或原模型环境。
合并后的 APK 只有 AndroidX 自有 signature 权限，没有 Internet、录屏、
跨应用悬浮或 Accessibility 权限。旧阶段检查见[Milestone 1 验证记录](docs/VERIFICATION_MILESTONE1.md)。

下面的 benchmark 与训练内容是保留的历史实验事实，不代表已认可模型可用。

**历史：现成多类别 detector 固定本地 benchmark 已执行；自研微调暂停。**
用户转交 ChatGPT 的正式结论为 `ATTEMPT02_VALID_BUT_DATA_LIMITED`。
本次 ZIP 读取环境异常，结论仅基于统计报告，不表示已经完成独立逐图或代码复审，
也不是可用 detector／泛化能力验收。ROI、数据、input 与训练预算同时改变，
不能把差异归因于某一个因素。

**Existing Multiclass Detector Local Benchmark** 已在独立环境执行唯一一次固定
confidence=0.1 的双 detector CUDA 推理：原顺序第一场 `natural_match_01`，
PTS 12..72s（不含 72s），4 FPS、240 帧；不是盲测。双模型延迟中位数
310.05ms、P95 332.99ms，实际运行 97.88s；这些是本机离线性能，不是实时资格。
原始 9,287 proposal → 合并 5,404 → 排除 86 个固定 UI proposal → 保留 5,318。
84 个 proposal labels 含塔、UI 和噪声，不是 84 个已确认 visual classes／卡牌；
输出尚待人工视觉复核，不能宣称识别可靠、泛化通过或直接采用该模型。
根仓库 MIT 不覆盖修改版 Ultralytics 的 AGPL 义务或权重／游戏素材权利。
公开 detector1 v0.7.13 文件的内部训练名为 v0.7.12；本 wrapper 明确使用
CUBIC，而上游位置参数实际为 LINEAR，因此不声称预处理字节级一致。保留本次结果，不重跑。
实际来源、环境和结果见[现成 detector benchmark 验证](docs/VERIFICATION_EXISTING_MULTICLASS_BENCHMARK.md)。
后续 primary／secondary 是视觉观察的语义职责，不是直接认定出牌；即使检测到
Witch，也不能直接产生 `OpponentCardPlayed`。历史 spawned Skeleton 仍只是视觉单位，
不等于 Skeleton 卡牌部署。候选权重权利仍为 `unverified`，私人本地 benchmark
不代表法律 clearance、素材／模型再分发或发布许可。
不执行 Attempt 03，不调整 confidence threshold／optimizer steps，不追加 Skeleton 标注，
不恢复普通亡灵专项门槛，不自动采用模型。该 benchmark 当时未进入 Module 3、Android 或实时 HUD；
当前另行授权的纯模拟 App 不包含真实游戏能力。
历史 benchmark 分支 `codex/existing-multiclass-local-benchmark`；当前分支
`codex/milestone2-apk-and-first-gt`，未 push／合并 main。

**已保留的历史：Attempt 02 唯一一次固定训练与 DEV_TUNE 评估。**
用户转交 ChatGPT 的 Attempt 01 独立结论为
`TWO_CLASS_SMOKE_ATTEMPT01_VALID_BUT_INSUFFICIENT`，保留原失败结果。
Attempt 02 固定 Nano 640 / batch 1 / FP32 / 300 steps；第一场仍为 TRAIN，
第四场现在只称 DEV_TUNE，不称盲测或独立测试。原两帧六个 TRAIN 框已核对，
本次新增 11 框确认、4 框拒绝。标准 TRAIN 为 14 帧（8 负／6 正）、15 框；
162s／165s partial 保留但不参与普通 loss，拒绝区域不作为 Negative。
旧锁不覆盖，新 expanded GT v2 与 ROI 导出均验证通过，训练框可视化已检查；
扩充帧不增加独立部署数。真实 GPU 完成恰好 300 步，checkpoint 回读成功。
固定诊断门槛下命中 2/5：Witch 2/2（分数仍极低），Skeleton 0/3。
68s 有 15 个采样帧误报；72s partial 的 4 个未匹配结果仍为 unjudged。
这是局部改善、仍不足以宣称可用的两类检测结果，不是识别能力验收通过；没有调参或重跑。
Attempt 02 训练轮的完整回归 908 passed / 3 既有权限 skipped，辅助检查 200 passed；
训练后的 32,217 个历史文件哈希、新快照和导出均保护通过，两个环境 pip check 通过。
本地结果 ZIP 已生成并校验；原结果保持不变，不进入 Attempt 03。
详见[Attempt 02 固定协议](docs/PHASE_C_ATTEMPT02_PROTOCOL.md)与
[当前准备记录](docs/VERIFICATION_ATTEMPT02_PREPARATION.md)。不 push、不合并 main。
人工确认后新锁和实际运行记录见[Attempt02 验证](docs/VERIFICATION_ATTEMPT02.md)。

**已保留的历史：Phase C 首次真实实验（Attempt 01）**：
Nano 416 / batch 1 / FP32 恰好 100 optimizer steps，之后仅一次两帧 DEV_VAL
评估。真实 GT → 导出 → CUDA 训练 → checkpoint 恢复链路成功；训练 loss 下降。
固定 IoU 0.5 下仅匹配 1/5 个 DEV_VAL GT，且该 Witch 分数极低；Skeleton 未匹配。
这是有效但检测能力明显不足的 smoke 结果，不是准确率验收通过。
保留首次结果，不调参、不重跑；其有效但不足结论已由用户转交的独立复核接受。
详见[固定协议](docs/PHASE_C_SMOKE_PROTOCOL.md)与[实际验证](docs/VERIFICATION_PHASE_C.md)。
下文原阶段的“不训练”边界属于历史，不撤销本次新授权。

本项目从用户主动提供的本地 MP4 开始，研究离线画面分析。
现有 **Module 1 离线录像读取工具**、**Module 2A1 证据准备工具**，以及
**Module 2A2 开发证据与实验锁工具**：
读取视频、导出完整 PNG、准备索引和联系表、校验人工证据并报告数据不足。
Module 2A1 已于 2026-10-04 正式验收，验收基准为
`98037ceba81683ad1a2c214bada30a10f2f3f69e`；并不代表可以开始训练模型。
Module 2A2 已于 2026-10-04 由用户确认正式验收，基准为
`69162023b87b71209f8dec9ebc9af69d4bfda944`；开发证据保持 DEV_LOCKED。
2026-10-05 用户确认 ChatGPT 已正式接受 2B-1 的失败实验结果，验收基准为
`585c3d95c832a1a86fce28ca822bc69d3646430f`，结论为
`MODULE_2B1_INSUFFICIENT_ACCEPTED`。这是**固定轻量模板基线不足**，不是模型
识别成功：两轮仍未达到 Top5/2 秒门槛，未生成 Model Lock。
2B-1 的验收记录和发布已完成。2026-10-05 用户暂停 **2B-2 普通亡灵专项数据补齐**，
不再以普通亡灵 4 场／8 次部署作为后续产品训练门槛；保留旧契约、标注工具和锁基础设施。
用户于 2026-10-05 报告 ChatGPT 对 **Module 2B-2A — Multi-class Dataset & Taxonomy Audit**
独立复核通过，结论为 `MODULE_2B2A_DESIGN_ACCEPTED_WITH_AMENDMENT`，
审查提交为 `cec8abc35fce2438d149fe4b68b203650cb835e4`；本轮补入 Scale Coverage Gate 并收尾设计阶段。
产品目标是每局动态出现的多种视觉单位，普通亡灵仅为历史样本和未来类别之一。
旧 pending 数据、录像完整性证据、2A2 锁与 2B-1 失败结果保留。
当前两类 smoke 分支已有 **2-Class Smoke GT Lock v1**：用户转交 ChatGPT 的精确人审确认，
11 个正例框（Witch 4 / Skeleton 7）、1 个拒绝项、4 个 appearance group；bbox 未改。
前三帧是所选两类的穷尽复核，72 秒帧仍有 Unknown；拒绝项不是 Negative。
此前 GT-only 阶段仅完成**人工 GT 冻结**，当时 `training_qualified=false`，
未创建 Training Dataset Lock；这段历史不是模型识别成功。
Witch/Skeleton 的 form=unknown 保留，spawned Skeleton 不解释为 Skeleton 卡牌部署。

已完成的数据阶段授权（2026-10-06）：只为上述 **Smoke GT Lock v1 的 11 个确认框**
准备并验证独立的 **2-Class Training Dataset Lock v1**，固定 match 01 / TRAIN、
match 04 / DEV_VAL、`unit.witch` / `unit.skeleton`，
`intended_use=private_local_research_poc`。
来源记录为 `source_type=user_recorded_gameplay`、`user_training_authorized=true`、
`external_upload=false`、`redistribution=false`、`rights_clearance=unverified`。
此处 `training_qualified` 只表示本项目内部的私人本地 PoC 门槛通过，不表示法律
clearance、Supercell 官方许可、商业用途或外部分发权利。当前已实际达到
`TWO_CLASS_TRAINING_DATASET_LOCKED`：独占 v1 创建、专用 readiness 与锁回读均退出 0，
新锁的 `training_qualified=true` 仅适用于上述内部范围；旧 GT-only v1 的 false 未回写。
1,462 个受保护既有文件哈希不变；此次新授权允许公开 GT／Dataset Lock 的
SHA，已记录于固定协议。素材哈希与私人文件仍只保留在本地。
本轮新增训练锁与原 GT 锁联合测试 **65 passed**（40 新增／25 原 GT），完整 maintained
回归 **908 passed / 3 既有 Windows 符号链接权限 skipped**，均退出 0，无失败／错误。
监督策略保留全部 11 框／4 帧，但默认完整所选类别监督
仅使用 3 帧／10 框；72 秒的第 11 个 Witch 正例标记为
`positive_only_requires_unknown_safe_consumer`，默认禁止普通全帧 loss／metrics，
不能把其 Unknown 区域当背景。
该数据锁阶段未训练、未下载权重、未进入 Phase C；本次训练的新授权见上方。
旧普通亡灵 target-recheck 产物保留为 **superseded / historical**；其 4 场／8 次
门槛不再是当前路线或 smoke 训练锁的前置条件。旧 2A2、2B-1、3–5 类 schema、
readiness 和锁继续保留原行为，不将新范围的资格写回旧锁。

2026-10-06 用户另行授权 **Phase B 模型环境资格验证**，现已达到
`MODEL_ENVIRONMENT_QUALIFIED`。独立环境使用 PyTorch 2.7.1+cu118、TorchVision
0.22.1+cu118、CUDA runtime 11.8，以及固定官方 YOLOX 0.3.0 源码
`6ddff4824372906469a7fae2dc3206c7aa4bbaee`。GTX 1050 Ti 4GB 实际执行 Nano
416 / batch 1 的三次合成 CUDA step，Tiny batch 1 和可选 Nano batch 2 也通过。
前向、loss/backward、非零参数更新、checkpoint 恢复、推理及 CUDA NMS 均成功，
没有 CPU assignment fallback。仅使用内存中的匿名随机张量，不读取真实 GT/图像训练，
不下载预训练权重。**环境可运行不等于检测成功或训练素材具备资格**。
该环境阶段未改变素材的 `training_qualified=false`；完整官方 Trainer、实际数据加载、长程训练、
ONNX/ncnn/移动部署均未验证。现有 `.venv` 与离线工具依赖不变。

原 3–5 类契约保持不变：**Module 2B-2B Phase A 数据工具已验证，原真实数据检查不足**；闭合
schema、独立 readiness、尺度政策、受检数据锁、人工标注、后端导出与独立命令入口
已通过各任务测试和本地代码复核。现有数据只读检查为有效但不足：四份录像、
75 张复用画面、8 个待确认单体框、0 个合格多类别候选；尚缺人工穷尽复核、
跨 TRAIN/DEV_VAL 支持、敌我对照、尺度覆盖及训练用途来源依据。
历史完整回归：**908 passed / 3 Windows 权限类 skipped**，退出 0；无 GUI 错误或跳过。
上一 GT-only 步骤检查 25 项通过，其完整回归为 908 passed / 3 既有权限 skipped。
已完成 Phase B 的完整回归 **908 passed / 3 skipped**，另有 16 项合成探针契约检查通过。
这不代表真实 Dataset Lock 或模型识别成功。类别从按原序复核的
Development 数据动态选择；先固定尺度政策、统计全部合格移动候选，再选至少一个
相对小移动类和一个中／大移动类。报告原图框像素尺寸及归一化面积分布；不足输出
`SIZE_COVERAGE_INSUFFICIENT` 并补 Development 素材，不恢复专项亡灵路线或降低门槛。
Nano/Tiny 仅完成合成运行资格，不以此比较真实检测效果；不恢复 Faster R-CNN 路线。
公开素材权利未明确，当前 reference_only。Phase A Task 1–6 与已完成的 Phase B
资格验证均保留各自证据；独立数据锁创建与验证已完成。本次用户另行授权
固定预算 Phase C；允许本地基线提交，仍不 push/merge。
旧 2A2 锁和 2B-1 失败结果不变。当前实际验证见
[阶段验证记录](docs/VERIFICATION_M2B2B.md)。
参见[研究审查](docs/research/2026-10-05-multiclass-dataset-taxonomy-audit.md)与
[已接受设计](docs/superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md)、
[设计收尾检查](docs/VERIFICATION_M2B2A.md)与
[Phase A 已授权实施计划](docs/superpowers/plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md)。
工具在 Windows 电脑上运行，不需要 Android Studio；尚无已验收的自动识别能力。

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
2A1 已完成验收记录及快进整合；其历史 `main` 基线为 `3ad657f…`，原功能分支保留。
用户于 2026-10-04 另行正式授权 Module 2A2 实施。当时 2B 尚未批准；
2026-10-05 当时的另行授权仅打开 2B-1；随后 2B-2 专项数据准备现已暂停，
当前两类 smoke 训练数据锁授权见本文开头。
Module 3 和真实游戏 HUD 仍未批准；当前 Android 仅允许上述纯模拟原型，
2A1 review 仍不代表新实验就绪。
参见 [Module 2A1 验证记录](docs/VERIFICATION_M2A1.md)。

## Module 2A2：独立证据与实验锁

本节记录 2A2 验收时的能力与授权边界；后续 2B-1 和当前 2B-2A 研究见本文开头。

本模块已授权，开发就绪与不可覆盖冻结基础设施已实现，不修改上述三条命令，
不训练或运行模型。用户当时再次人工确认四份录像覆盖完整自然对局，并明确修改
“完整回放”定义：**用户确认覆盖完整对局，实际解码末帧作为可评估结束边界**。
不再要求出现胜利／失败结算画面；记录 `completion_attestation=user_confirmed`、
`terminal_result_screen_present=false`，后者不阻止 Development Data Freeze。
仍拒绝损坏、无法解码、明显中途截断、关键战斗缺失或人工明确不完整的录像。
此前结算画面驱动的排除结论已被本次授权取代，旧检查及素材不删除、不覆盖。
已按原清单从第一份完成开发证据冻结：复用 37 张定位画面和原人工粗复核，
仅在新的忽略路径补充定位／关键画面。用户通过局部原图纠正卡牌身份后，目标为
普通“亡灵”（minions，三只），不是亡灵大军；两次独立部署、六张原始关键框。
四个候选数据包保留其他卡牌的未知形态／疑点，三个明确未知区间、零负样本。
readiness / freeze-development / validate-lock 均退出 0，2A2 验收停点为 DEV_LOCKED，
当时没有进入 2B。`user_confirmed` 的共享完整区间由代码严格绑定到
`0..recording.last_frame_seconds`，未知尾段不能代替完整边界；仍不要求结算 UI。

新增独立实验命令：`readiness`、`freeze-development`、`validate-lock`、
`freeze-test-gt`。最后一条仅提供未来盲测契约，当前未开展真实测试／模型工作。
修复完整回归为 406 项通过、1 项 Windows 权限跳过，依赖检查通过。
验收整合前的 912 个既有受保护文件哈希不变；录像、索引、报告、标注和锁仍被 Git 忽略。
完整性来源字段和首末边界修复没有改变旧 prepare / validate / review 语义。
当时用户只授权验收记录、快进整合与推送；不包含新录像处理、模型锁、测试标注锁或 2B。
本地打包是此前基础设施阶段的结果，本次没有重跑构建。完整复核记录见下方文档。
命令细节见数据契约，无需你手动编写标注 JSON。

第一轮改为：一场**新的自然开发对局**，人工整局复核后从对手实际用过的卡中选
一个明确形态，至少两次清晰独立部署；没有合格目标就换下一场自然对局，不降低
标准。旧地狱飞龙录像只用于历史回归，不能默认沿用为第一张模型目标。
普通、觉醒和未知形态分开；未知区间及另一形态不能作为负样本。

开发数据锁定与 2A2 验收已完成；当时另行授权仅覆盖 2B-1 开发基线，
随后 2B-2 专项数据准备曾获批准，现已暂停；两类 smoke 数据锁已创建验证。
当前已单独授权上方固定预算 Phase C，不包含盲测。
后续顺序为：开发锁 → 模型锁 → 独立
测试录像及新会话人工标注 → 测试标注锁 → 首次整场模型推理；不得先看预测再改
标签。同一真实比赛即使重录或换文件，也不能跨开发/测试。

### 下一份录像怎么准备

仅供后续另行授权的新输入参考，本轮不需要新增录像，也不执行下面的准备命令。

正常打一场游戏，结束后从**对战记录打开完整回放**，用系统录屏覆盖整局，
正常速度，不剪辑、不倍速、不安排对手。无需提前挑卡。
建议多留几秒方便定位，但是否拍到结算 UI 不再是完整性门槛；无需仅因此重录。
明显中途截断／关键战斗缺失仍不能用于冻结，发现具体冲突要先核实。
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

## Module 2B-1：普通亡灵轻量视觉基线

只用现有冻结开发数据：一场对局、两次独立部署、六张组合框。多尺度模板匹配
搜索完整战场，ORB 仅作诊断；先保存两轮排名，再评分隐藏部署，未调参重跑。
适配层在扫描前已载入两次部署元数据和参考裁切；每折 scan/rank 仅使用该折参考
和固定配置。这是函数输入分离，不是延迟加载隐藏元数据或进程／会话隔离；
此限制已在 Review Packet 中披露，本次不修改实现或原实验协议。
A→B 排除参考部署后无候选；B→A 仅有一个候选，首次支持延迟 4.75 秒，超过
原定 2 秒限制。相似度分数不是识别正确概率；这些结果不证明跨对局能力。

独立入口为 `python -m clash_tracker_video.baseline_io`：`crossval` 成功退出 0，
基线不足退出 3，参数或证据错误退出 2；`build` 仅允许两轮通过后执行；
`validate-lock` 核对真实 detector JSON、原图裁切与 Model Lock 的完整处理参数。
2B-1 当时未执行 PASS-only build、测试标注或独立测试；未进入 2B-2，也未训练模型。
Module 1 与 2A1 三条命令和 `experiment_gate=false` 语义不变。

独立验收接受的是原始 `2B1_BASELINE_INSUFFICIENT` 结果，不是 PASS 或识别性能认证。
2B-1 收尾完整回归重新验证 474 项通过、1 项权限跳过，依赖检查通过。配置及两轮
失败证据保留，不重新运行真实识别、不生成 Model Lock、不降低门槛或将未知区间
当负样本。其后用户仅授权 2B-2 数据准备；训练、独立盲测和后续模块仍需另行授权。
参见 [协议](docs/MODULE_2B1_PROTOCOL.md) 和
[实际验证记录](docs/VERIFICATION_M2B1.md)。

## Module 2B-2 第一阶段：历史数据准备（已暂停）

采用独立的 `minion_unit` 数据契约，不改旧 Development Lock、组合框或 2B-1
失败结果。目标卡、视觉单位和独立出牌分别记录；同一比赛的不同录像、连续帧和
多个单位框不能制造更多比赛或部署。数据就绪不等于评价时间覆盖就绪，更不授权训练。
当前代码仅保留在本地功能分支，未推送、未合并。窗口工具验证及真实数据准备进度见
[阶段验证](docs/VERIFICATION_M2B2_DATA.md) 和
[数据契约](docs/MODULE_2B2_DATASET_CONTRACT.md)。

独立入口为 `python -m clash_tracker_video.training_dataset_cli`，包括
`validate-dataset`、`freeze-dataset`、`validate-dataset-lock`、`annotate`。
验证：就绪 0、有效但不足 3、错误 2；冻结：成功 0、不足／错误／重复版本 2。
标注窗口关闭的 0 仅表示会话结束，不代表已保存、审核或冻结。
真实 pending 草稿通过加载，返回 3；72 张待审核图片、零单位框、零训练支持、
零认证缺席时长。两个门槛均为 false；未知内容不是负样本，也没有 FP/min 结论。
原片段、既有标签与此前完整性声明均保留。后续 bounded target-recheck 已确认第二份
中途截断且没有后续片段，并在新的私有修订中排除其训练用途；第三／四份采样复核
未新增确认的普通亡灵部署。这些产物保留为 superseded / historical，不证明整局无目标。
用户已暂停普通亡灵专项路线，本轮不继续此复核或要求补足 4 场／8 次。旧 validator
保留原行为，只验证历史固定类别契约，不能当新多类别 readiness；新多类别 Phase A
另有独立契约与工具，不复用旧门槛。

## 项目事实源

- [项目定义](PROJECT.md)
- [当前状态](docs/CURRENT_STATE.md)
- [决策](docs/DECISIONS.md)
- [开发计划](docs/DEVELOPMENT_PLAN.md)
- [Module 1 验证与依赖来源](docs/VERIFICATION_M1.md)
- [协作约束](AGENTS.md)
