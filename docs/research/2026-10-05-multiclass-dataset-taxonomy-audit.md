# Module 2B-2A — Multi-class Dataset & Taxonomy Audit

审查日期：2026-10-05。性质：公开资料研究与设计依据，**不是模型实验或训练授权**。
本地实现基线：`f0b424a0aa78079840ecc665e362023ee81042ce`。
分支：`codex/module-2b2a-taxonomy-audit`。不合并、不推送。

## 1. 结论与边界

- 产品要识别每局出现的多种视觉单位，而非持续扩充一个固定普通亡灵类别。
  一套有版本的类别全集，支持每局动态出现的子集；不意味着能够识别任意未知卡。
- 公开项目确有真实标注截图、切片资产与合成工具。它们可帮助设计标签与数据流程，
  但本轮无法确认游戏画面、视频作者及权重的完整训练／再分发权利链，列为
  `reference_only`，不导入正式训练集。
- upstream README 的 154 类、代码中的 155 标签、126 个卡牌条目和数千张图片，
  都不是当前游戏完整卡牌数，也不是独立比赛／部署数。
- 优先建议后续资格验证 YOLOX Nano，再考虑 Tiny；Faster R-CNN MobileNetV3-FPN
  保留为桌面比较方案。没有选定或安装新模型，也没有实测 4GB 显存能否承受。
- 新 PoC 与标签设计见[待复核设计](../superpowers/specs/2026-10-05-module-2b2a-multiclass-design.md)。
  旧 2A2 锁、2B-1 失败结果、2B-2 工具与私人数据不修改。

## 2. 方法、快照与可信度

通过 GitHub 官方 API 的提交、完整树与文本文件，以及官方模型／政策文档进行只读审查。
GitHub CLI 可用；agent-reach CLI 不存在，使用其 GitHub 官方接口路径，没有安装工具。
读取 README、LICENSE、类别／状态注册表、标注转换与划分代码、合成／检测／导出配置。
未下载图片、视频、数据包或权重，未执行外部仓库代码，未连接任何游戏账号。

| 资料 | 固定审查快照 | 审查角色 |
|---|---|---|
| Clash-Royale-Detection-Dataset | `31b4151fedb1b914e99c3c122c16dca61cb2b905` | 文件结构、标注与素材来源 |
| KataCR | `36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8` | 类别、状态、生成器与检测器 |
| 旧 Clash-Royale-Dataset | `7df93642047d4df541225755bca61c301788bebe` | 解释历史 116 卡／127 单位描述，不作为新增训练来源 |
| YOLOX | `6ddff4824372906469a7fae2dc3206c7aa4bbaee` | Nano/Tiny 配置及官方部署示例 |
| TorchVision | `7a7520f83957fe6a0f934fe7035f07b5ef32e8f9` | Faster R-CNN 配置、许可证与权重说明 |

事实分三级：**文件／代码确认**、**作者文档声明**、**本项目推断／建议**。
文件树证明文件存在，不证明标签准确、比赛独立、资产权利或权重下载链接有效。
2024 年数据快照不是 2026 年完整游戏分类表；本轮不追认新增卡／觉醒版本。

## 3. 公开数据实际包含什么

Dataset 完整 Git 树未截断：27,041 个条目，26,798 个文件。按固定路径统计：

| 对象 | 实际数量 | 含义与限制 |
|---|---:|---|
| `images/part2` JPG | 7,380 | 包含不同来源和背景；不是 7,380 次独立部署 |
| 同目录 JSON / TXT | 6,966 / 6,972 | 两种标注文件；不能仅按图片数宣称都有标注 |
| JPG+JSON+TXT 同 stem 三件套 | 6,966 | 真实文件结构可用；未逐图审查质量／完整性 |
| `images/segment` 图片 | 4,654（4,627 PNG，27 JPG） | 单位／特效切片及背景，不是独立自然样本 |
| segment 目录 | 154；非背景 152 | 包括 `big-text` / `small-text` 别名，不等于模型类别数 |
| KataCR 注册标签 | 155，ID 0..154 | 与组合检测器 YAML 一致，混合单位、UI、特效、塔等 |
| 分检测器标签数组 | 85 / 85 / 65 | 有重叠，不能相加成 235 个独立类别 |
| `card_list.py` 扁平卡牌条目 | 126 | 代码注释 125 已滞后；卡牌表不等于视觉标签表 |

来源目录包含 OYASSU、WTY、lan77 及日期／episodes 标识，说明有自然截图来源的
组织结构，但目录名不能独立证明原视频 URL、来源作者授权或 underlying match identity。
作者文档说明视频来自 YouTube 或自录；原视频不随该仓库发布。标注日志涉及人工
标注／纠错、检测器辅助与 SAM 切片，不能把所有标签自动描述成纯人工独立 GT。

150 个注册标签有同名 segment 目录。缺少同名切片的是 `mirror`、`selected`、
`tesla-evolution-shock`、`text`、`zap-evolution`；文本使用两个别名目录。
这只描述该快照资产布局，不证明这些类别不可能被检测。

KataCR 有基于这些切片／背景的合成生成器；生成物仍继承输入资产的权利与域差异。
本轮没有运行生成器，也不把源仓库所有截图称为合成图或宣称已有合成训练锁。
两仓库树中未发现 `.pt/.pth/.onnx/.ckpt/.safetensors` 权重文件。
KataCR README 另给两个 Google Drive 检测器链接（v0.7.13）；仅核对链接和代码引用，
没有下载、解包、加载、校验 SHA 或独立验证训练来源。

主要依据：[Dataset README](https://github.com/wty-yy/Clash-Royale-Detection-Dataset/blob/31b4151fedb1b914e99c3c122c16dca61cb2b905/README_en.md)、
[标注日志](https://github.com/wty-yy/Clash-Royale-Detection-Dataset/blob/31b4151fedb1b914e99c3c122c16dca61cb2b905/Images%20annotate%20logs.md)、
[类别注册表](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/constants/label_list.py)、
[卡牌表](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/constants/card_list.py)、
[组合检测器配置](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/yolov8/detector_combo/data.yaml)。

### 3.1 完整 upstream 标签清单

以下是上述固定注册表的 155 个事实性名称，按原始顺序排列。保留 upstream 拼写，
**不是本项目已接受的 canonical taxonomy**，也不对当前游戏覆盖程度作承诺。

```text
king-tower, queen-tower, cannoneer-tower, dagger-duchess-tower, dagger-duchess-tower-bar
tower-bar, king-tower-bar, bar, bar-level, clock
emote, text, elixir, selected, skeleton-king-bar
skeleton, skeleton-evolution, electro-spirit, fire-spirit, ice-spirit
heal-spirit, goblin, spear-goblin, bomber, bat
bat-evolution, zap, giant-snowball, ice-golem, barbarian-barrel
barbarian, barbarian-evolution, wall-breaker, rage, the-log
archer, arrows, knight, knight-evolution, minion
cannon, skeleton-barrel, firecracker, firecracker-evolution, royal-delivery
royal-recruit, royal-recruit-evolution, tombstone, mega-minion, dart-goblin
earthquake, elixir-golem-big, elixir-golem-mid, elixir-golem-small, goblin-barrel
guard, clone, tornado, miner, dirt
princess, ice-wizard, royal-ghost, bandit, fisherman
skeleton-dragon, mortar, mortar-evolution, tesla, fireball
mini-pekka, musketeer, goblin-cage, goblin-brawler, valkyrie
battle-ram, battle-ram-evolution, bomb-tower, bomb, flying-machine
hog-rider, battle-healer, furnace, zappy, baby-dragon
dark-prince, freeze, poison, hunter, goblin-drill
electro-wizard, inferno-dragon, phoenix-big, phoenix-egg, phoenix-small
magic-archer, lumberjack, night-witch, mother-witch, hog
golden-knight, skeleton-king, mighty-miner, rascal-boy, rascal-girl
giant, goblin-hut, inferno-tower, wizard, royal-hog
witch, balloon, prince, electro-dragon, bowler
executioner, axe, cannon-cart, ram-rider, graveyard
archer-queen, monk, royal-giant, royal-giant-evolution, elite-barbarian
rocket, barbarian-hut, elixir-collector, giant-skeleton, lightning
goblin-giant, x-bow, sparky, pekka, electro-giant
mega-knight, lava-hound, lava-pup, golem, golemite
little-prince, royal-guardian, archer-evolution, ice-spirit-evolution, valkyrie-evolution
bomber-evolution, wall-breaker-evolution, evolution-symbol, mirror, tesla-evolution
goblin-ball, skeleton-king-skill, tesla-evolution-shock, ice-spirit-evolution-symbol, zap-evolution
```

### 3.2 普通／觉醒、单位／法术、归属

注册表有 16 个 `-evolution` 标签：skeleton、bat、barbarian、knight、firecracker、
royal-recruit、mortar、battle-ram、royal-giant、archer、ice-spirit、valkyrie、bomber、
wall-breaker、tesla、zap。另有觉醒提示符和 shock 特效；提示符不是单位的新部署。
无后缀名称不能自动证明当前版本的普通形态，导入时仍需 form 证据。

upstream 分类子集彼此重叠且存在遗漏：ground 115、flying 21、tower 4、spell 16、
other/UI 12、object 4、background-item 15。**不能将这些数字相加**。
spell 子集包含技能／shock，缺少另列的 `zap-evolution`；UI 子集未包含 `selected`。
历史 `state_list.py` 也不是覆盖当前注册表的完整 ontology。

spell 子集：arrows、clone、earthquake、fireball、freeze、giant-snowball、goblin-barrel、
graveyard、lightning、poison、rage、rocket、skeleton-king-skill、tesla-evolution-shock、
tornado、zap。object 子集为 axe、dirt、goblin-ball、bomb。短时法术与飞行投射物要
单独建模；不因它们列在标签表就认为已有可靠出牌识别。

标注转换输出 `class,cx,cy,w,h,state0..state6`，共 12 列，坐标归一化。
side 0/1 表示 friend/enemy；当前 `num_state_classes=1`，检测器主要预测 side，
其余状态槽保留历史语义，不代表七类状态均已可靠学习。缺失状态默认零，不能把
默认零误当人工确认“我方”。归属来自状态，不是把每种单位复制成 enemy 名称。

标注构建器随机打乱帧并分 train/val，存在相邻帧／同场比赛泄漏风险。
其划分不能直接用作本项目独立测试；来源授权明确后也必须按 underlying match 重建。
依据：[状态表](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/constants/state_list.py)、
[标注构建器](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/build_dataset/label_builder.py)。

### 3.3 卡牌与视觉单位不能一一对应

| 关系 | 标签／映射示例 | 本项目后果 |
|---|---|---|
| 多卡 → 同类单位 | minions / minion-horde → minion；musketeer / three-musketeers → musketeer | 单框无法确定来源卡／费用 |
| 一卡 → 多类单位 | rascals → rascal-boy + rascal-girl | 类别数不等于出牌次数 |
| 阶段变化 | golem / golemite；elixir-golem big/mid/small；phoenix big/egg/small | 变形／死亡衍生不能自动记新出牌 |
| 召唤／法术衍生 | skeleton、goblin、barbarian 等共享视觉单位；技能与投射物另有标签 | 需独立因果／来源证据，不能看到单位就扣圣水 |

这些是 upstream 标签／卡牌映射暴露出的建模问题，不是已审核的 2026 全卡规则库。
`unit2cards` 仅覆盖少量映射，不足以作为完整反向识牌表。
首轮多类别 detector 只输出 VisualObservation，不产生 OpponentCardPlayed。

## 4. 独立 License / Provenance Audit

这是工程风险筛查，不是法律意见或 Supercell 许可。`reference_only` 指不得把材料
纳入正式训练／再分发，不妨碍只读学习事实与算法。权重一律保持 use-gated。

| 对象 | 可核对的许可／来源 | 未被证明的权利 | 当前处理 |
|---|---|---|---|
| 两个 wty-yy 仓库的软件 | 根 LICENSE：MIT，2024 wty | 作者不能据此授予第三方游戏资产权利 | 可参考软件；复用需保留声明并逐文件检查 |
| 真实 JPG / JSON / TXT | YouTube／自录声明，来源目录与标注日志 | 游戏资产训练、再分发／商业使用；各视频作者授权链 | reference_only，未下载训练材料 |
| segment / 背景与合成数据 | 游戏截图切片，SAM 辅助，合成器可见 | 合成不消除原素材权利；没有逐资产授权清单 | reference_only |
| KataCR YOLOv8 路线 | 依赖 ultralytics 8.1.24；文件有 AGPL 标识／导入 | 根 MIT 不覆盖依赖的 AGPL／商业授权条件 | 不直接复用该模型栈作为新默认 |
| Drive v0.7.13 检测器 | README 两个链接，组合检测器引用文件名 | 文件 SHA、完整训练清单、权重许可、上游资产权利 | reference_only / use-gated，未下载 |
| SAM | Meta 软件／官方模型 Apache-2.0；SA-1B 数据另有条件 | 作者实际权重来源／SHA；游戏切片权利不会因 SAM 改变 | 只参考流程 |
| YOLOX 软件 | Apache-2.0 | official COCO 权重不能仅凭代码许可推定权利链完整 | 代码候选；权重单独核准 |
| TorchVision 软件 | BSD-3-Clause | 检测权重及 ImageNet backbone 的数据／使用条件独立 | 代码候选；权重单独核准 |
| ncnn | BSD-3-Clause，第三方组件另有声明 | 转换不改变模型权利或数据权利 | 后续部署候选 |
| 用户自录画面 | 用户明确授权当前本地离线分析 | 不等于 Supercell 商用资产／训练集公开授权 | 保持本地；用途扩展仍需核准 |

KataCR 的训练配置 `pretrained: False` 只描述该文件，不证明链接权重确按此配置训练。
Ultralytics 8.1.24 源许可为 AGPL-3.0，当前官方另提供 Enterprise 选项；不能说根 MIT
抹除下游条件，也不能简单说 AGPL 一律禁止商业使用。路线选择应计入合规成本。

YouTube 标准发布许可不自动授权任意复用；CC BY 需要明确标识，平台不能授予其他
权利人的许可。Supercell Fan Content Policy 提供有条件的粉丝内容规则，包括应用／
视频限制，不等于明确授予通用 ML 训练、合成素材包或商用 detector 权利。
未来下载前应记录每类材料的 URL、版本、许可文本、来源作者、资产权利依据、允许用途
与再分发条件；不明确则不纳入正式训练。即便依法获得素材使用权，也不代表实时
游戏辅助获得许可；实时安全门槛不变。

许可主要证据：

- [Dataset MIT](https://github.com/wty-yy/Clash-Royale-Detection-Dataset/blob/31b4151fedb1b914e99c3c122c16dca61cb2b905/LICENSE)、[KataCR MIT](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/LICENSE)。
- [KataCR requirements](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/requirements.txt)、[训练配置](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/yolov8/ClashRoyale.yaml)、[组合检测器](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/yolov8/combo_detect.py)。
- [Ultralytics 8.1.24 LICENSE](https://github.com/ultralytics/ultralytics/blob/a7cfd83c5f6ce2b9d73db62a0a15f2041fbe0bb7/LICENSE)、[官方许可说明](https://www.ultralytics.com/license)。
- [SAM 官方声明](https://github.com/facebookresearch/segment-anything/blob/dca509fe793f601edb92606367a655c15ac00fdf/README.md)、[游戏切片脚本](https://github.com/wty-yy/KataCR/blob/36ceb9fcfbd117c2ce3d97eacee435c1898eb7b8/katacr/build_dataset/segment.py)。
- [YouTube 许可说明](https://support.google.com/youtube/answer/2797468?hl=en)、[Supercell Fan Content Policy](https://supercell.com/en/fan-content-policy/)、[服务条款](https://supercell.com/en/terms-of-service/)。
- [TorchVision 模型及权重条件](https://docs.pytorch.org/vision/stable/models.html)、[COCO 数据条件](https://github.com/cocodataset/cocodataset.github.io/blob/master/dataset/termsofuse.htm)、[ImageNet 下载条件](https://www.image-net.org/download.php)、[YOLOX 权重发布页](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0)。
- [TorchVision BSD-3-Clause](https://github.com/pytorch/vision/blob/7a7520f83957fe6a0f934fe7035f07b5ef32e8f9/LICENSE)、[YOLOX Apache-2.0](https://github.com/Megvii-BaseDetection/YOLOX/blob/6ddff4824372906469a7fae2dc3206c7aa4bbaee/LICENSE)、[ncnn LICENSE](https://github.com/Tencent/ncnn/blob/c7ad4fc6a8393adcb6ca285157ca484d070646dd/LICENSE.txt)。

## 5. 重新比较检测模型

下表数字来自官方 COCO 资料，不是 Clash Royale、GTX 1050 Ti 或手机实测。
不同输入尺寸／实现的 FLOPs、AP 不能直接当同条件速度或小目标准确率比较。

| 方案 | 官方规模／COCO 数字 | 多类别与小目标 | 4GB 与部署评估 |
|---|---|---|---|
| Faster R-CNN MobileNetV3-Large-FPN | 19.39M 参数；74.2MB 权重；AP 32.8；4.49 GFLOPs；默认短边 800 | 任意自定义类别，ID 包含背景；FPN/两阶段适合作比较，但小单位能力须实测 | activation/proposal/ROI 内存风险；ONNX 固定 batch/尺寸路径及 ROIAlign/NMS 算子验证成本；无本项目移动实测 |
| 同系列 320-FPN | 同样 19.39M／74.2MB；AP 22.8；0.72 GFLOPs；短边 320，长边上限 640 | 不是更少参数的新模型；降尺寸可能损失小单位像素 | 可降计算但不保证训练显存够；不能把其低 FLOPs 套到 800 版本 |
| YOLOX Nano | 0.91M；1.08G；AP 25.8，416 输入 | 可改类别数；stride 8/16/32，depthwise；微小单位仍可能欠采样 | 优先资源资格验证候选；官方 ONNX / ncnn / Android 示例存在，但不是即用 APK |
| YOLOX Tiny | 5.06M；6.45G；AP 32.8，416 输入 | 容量较大，仍须针对密集小目标验证 | 若 Nano 在开发集不足且资源允许，才比较 Tiny；不保证 4GB 或手机实时 |

TorchVision detection API 标为 Beta，使用专有 C++ 算子；其 builder 在
`weights=None` 时仍可能默认加载 ImageNet backbone，未来未授权时必须同时禁用
`weights_backbone`，不能把模型初始化当不会下载的检查。

YOLOX 默认训练 random_size 范围对应 320–640，不能用 416 的公开数字保证显存。
官方 ONNX 脚本涉及旧 `torch.onnx._export`／opset，动态 batch 不等于任意尺寸已支持。
ncnn 示例需处理 Focus 层及模型参数转换；C++ 示例有固定输入、COCO 类别表和
不区分类别的 NMS 路径，Android 示例较旧。后续须核对输出布局、类别／owner 编码、
缩放、坐标恢复、class-aware NMS 与数值一致性，不盲复制示例。

主要依据：[TorchVision 常规版](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.detection.fasterrcnn_mobilenet_v3_large_fpn.html)、
[320 版](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.detection.fasterrcnn_mobilenet_v3_large_320_fpn.html)、
[YOLOX 官方表](https://github.com/Megvii-BaseDetection/YOLOX/blob/6ddff4824372906469a7fae2dc3206c7aa4bbaee/README.md)、
[ONNX 脚本](https://github.com/Megvii-BaseDetection/YOLOX/blob/6ddff4824372906469a7fae2dc3206c7aa4bbaee/tools/export_onnx.py)、
[ncnn 转换说明](https://github.com/Megvii-BaseDetection/YOLOX/blob/6ddff4824372906469a7fae2dc3206c7aa4bbaee/demo/ncnn/cpp/README.md)、
[ncnn 检测示例](https://github.com/Megvii-BaseDetection/YOLOX/blob/6ddff4824372906469a7fae2dc3206c7aa4bbaee/demo/ncnn/cpp/yolox.cpp)。

### 5.1 GTX 1050 Ti 4GB：框架兼容与显存是两个问题

该卡属 Pascal／compute capability 6.1。不能默认最新 CUDA wheel 支持它。
当前 PyTorch release matrix 的 2.14 / CUDA 12.6.3 列出 Pascal 支持；12.8/12.9
构建已移除此架构，2.15 的 CUDA 12.6 wheel 也计划停止。候选需按版本冻结并实测
实际 compiled architectures／驱动／算子，不能把表中的 sm_60 直接当本机验证 sm_61。
可研究 2.14 + TorchVision 0.29 + cu126 的资格验证组合，但 **本轮未安装且不作为锁定环境**。
YOLOX 老代码与 Python 3.12／当前 PyTorch 的组合也需单独验证。

未来经授权后使用隔离环境，不升级现有固定 `.venv`。先做小输入、batch 1 的显存／
算子 smoke test，再决定是否训练。固定输入／冻结部分层等是待验证降资源选项，
不是已跑通训练方案；Pascal 不具现代 Tensor Core，不能默认 AMP 有明显加速。

依据：[NVIDIA Pascal 型号说明](https://nvidia.custhelp.com/app/answers/detail/a_id/5678/~/list-of-maxwell,-pascal-and-volta-series-geforce-gpus)、
[NVIDIA 1050 Ti capability 讨论](https://forums.developer.nvidia.com/t/geforce-gtx-1050ti/53329)、
[PyTorch release matrix](https://github.com/pytorch/pytorch/blob/4adc5dee90432ca3c13a9386e7732fdd08f054e1/RELEASE.md)、
[CUDA 12.8/12.9 架构变更](https://dev-discuss.pytorch.org/t/cuda-toolkit-version-and-architecture-support-update-maxwell-and-pascal-architecture-support-removed-in-cuda-12-8-and-12-9-builds/3128)、
[2.15 cu126 停止公告](https://dev-discuss.pytorch.org/t/notice-cuda-12-6-wheels-will-no-longer-be-published-from-pytorch-2-15-drops-maxwell-pascal-volta/3432)。

### 5.2 建议与未解决问题

推荐顺序是 **Nano 资源资格验证 → 必要时 Tiny 开发比较**。Faster R-CNN 为桌面参照，
不是继续强制的旧选型。此顺序综合软件许可、轻量化与官方移动路径，属于推断，
不证明 Nano 比 Faster 更准。未解决事项是素材／权重用途依据、当前框架兼容、
真实小目标表现、所有权混淆、ncnn 数值一致性与手机性能，均需后续独立授权与证据。

## 6. 本轮交付与验证边界

交付公开研究记录、待审设计及当前状态／路线变更文档。无源码、测试、依赖、
schema 实现或私人 Evidence 改动；旧 4 场／8 次校验仍在历史实现中，不作为新路线门槛。
本轮只检查文档、引用、Git 范围、依赖一致性和现有私人文件保护，结果写入当前状态。
以前的 680 passed / 2 skipped 是旧数据阶段结果，**不是本轮重新执行**。
模型安装、训练、推理、性能评测、模型导出／Android Build：Not Run，未授权。
独立子任务审查不是 ChatGPT 独立验收；设计与新门槛等待其复核及用户后续批准。
