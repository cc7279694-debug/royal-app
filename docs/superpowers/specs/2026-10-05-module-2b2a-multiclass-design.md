# Module 2B-2A — Multi-class Dataset & Taxonomy Design

Status: **ACCEPTED WITH AMENDMENT — design stage closed** (2026-10-05).
用户报告 ChatGPT 对 `cec8abc35fce2438d149fe4b68b203650cb835e4` 的独立设计复核结论：
`MODULE_2B2A_DESIGN_ACCEPTED_WITH_AMENDMENT`。本轮补入 Scale Coverage Gate；
这记录用户交付的验收结论，不声称本轮重新取得 ChatGPT 的审查回复。
本文件是已接受的设计要求；不是多类别代码已实现、数据已就绪、选型已实测或训练授权。
事实与许可证依据见[公开资料审查](../../research/2026-10-05-multiclass-dataset-taxonomy-audit.md)。

## 1. Task Contract

**Goal:** 建立可扩展的多类别视觉标签与可信的最小实验设计，服务每局动态出现的
对手视觉单位。普通亡灵是历史样本／未来类别之一，不再是产品固定标准。

**Scope:** 审查公开资料；提出 taxonomy、schema、数据／许可边界、模型候选与
多类别 PoC；同步当前文档。暂停旧亡灵 4 场／8 次专项，不删除旧工具与契约。

**Out of scope:** 安装模型、下载训练资产／权重、训练／推理、修改真实标注／数据／
锁／旧失败结果、Model Lock、Module 3、卡序／圣水、Android、HUD、实时或游戏控制。

**Constraints:** Local-first；输入按既定自然录像顺序；比赛而非文件作 split identity；
Unknown 非 Negative；监督标注在预测前锁定；视觉 observation 非出牌 event；
实时许可门槛不变。旧实现没有被本设计偷偷放宽。

**Dependencies:** Module 1 的实际 PTS／原图抽帧，2A1 安全加载，2A2 独立比赛与
不可覆盖锁语义，2B-2 逐只标注／分组基础设施。无数据库或存储迁移要求。

**本轮 Acceptance:** 公开类别／数量／状态可追溯；代码、素材与权重许可分开；
schema 明确 many-to-many 与未知语义；比较两条模型路线；提出预先固定的未见比赛
PoC；保护现有数据；提交可交给 ChatGPT 的设计，随后停止。

## 2. 路线选择

1. **推荐：本地人工多类别数据 + 轻量检测候选。** 对开发自然比赛确认小类别集合，
   单框多类别监督，后续经授权比较 Nano/Tiny。素材用途仍需明确；不宣称自录即权利清除。
2. 直接使用 KataCR 数据／权重：覆盖广，但授权链、frame-level split、过时类别与
   AGPL 依赖复杂。当前只参考，不能作为正式训练捷径。
3. 从一开始做全类别／源卡恢复：召唤与变形、普通／觉醒、短时法术使目标过大。
   暂不采用；先证明多类单位能够跨自然比赛识别，再另行做部署与卡牌归因。

模型建议是资格验证顺序，不是已实测并锁定的选型。新方案不受历史 Faster R-CNN 决定约束。

## 3. 统一视觉标签 Schema（已接受设计，未实现）

新增独立 contract kind：`multiclass_visual_dataset`、schema_version=1。
不要向旧固定字段 schema 塞新字段或重写旧锁；使用新的 validator／readiness／lock
入口。复用通用安全解析、PTS 和媒体绑定能力，不复用旧 minions/normal 就绪门槛。

| 层 | 必需字段／语义 | 关键约束 |
|---|---|---|
| Taxonomy | taxonomy_id/version；visual_class_id；kind；mobility；definition；alias mapping | ID 稳定、有版本；mobility=moving/static/unknown，与模型整数 ID 分离 |
| Kind | unit / building / spell_effect / projectile / battlefield_object / ui | UI 可保留定位元数据，默认不是首轮检测目标 |
| Observation GT | annotation_id、frame_id、visual_class_id、owner、observed_form、box、review_state | 一只可见实体一框；不自动推断出牌 |
| Owner | own / opponent / neutral / unknown；perspective_ref | 不由上下半场或默认数值推断；参考视角变化需声明 |
| Form | normal / evolved / unknown；可选 visual_stage | 未知非普通；阶段如 phoenix egg 与觉醒不同 |
| Source card | source_card_id 可空、source_card_candidates、mapping_basis/verification | 多对多，NULL 合法；不从单框强行恢复费用／卡名 |
| Group identity | underlying_match_id、recording_id、appearance_group_id | 同场重录不独立；一群单位／连续帧不增独立支持数 |
| Causal / event | origin_kind、可空 human_deployment_id／parent_group_id／entity_occurrence_id | direct / summoned / transformed / unknown；不知道因果就保留未知 |
| Frame binding | raw_pts、time_base、origin、frame_id、image metadata/hash | 与旧实际 PTS／原图身份一致，平均 FPS 不替代 PTS |
| Coverage | exhaustive_for_classes、reviewed_regions、unknown intervals、ignore reasons | 缺省未标注不是不存在；空框须明确穷尽复核 |
| Provenance | source_id、creator/source URL、artifact kind、license evidence、allowed_scope | 代码／数据／游戏资产／权重分别审核；不明确 reference_only |
| Split | underlying match → train / development_validation / prospective_test | recording／裁切／增强继承比赛分组，无跨 split 派生 |

示例 canonical ID 可为 `unit.minion`、`unit.musketeer`、`building.cannon`、
`spell_effect.fireball`、`projectile.axe`。这只是命名规则，不是已选择的首轮类别。
`unit.minion` 可以来自不同卡；卡牌来源未知时仍能有可信视觉 class。
种类、owner、form 必须各自保留证据，不把场上同类单位简单标成一次新 deployment。

box 使用旋转校正后的完整原图、归一化 `x/y/width/height`，四值与图像尺寸严格校验。
紧贴可见实体范围，不猜遮挡身体，不把阴影／光束算入单位框；occlusion/truncation
单独记录。战场 ROI 只是模型变换，输出恢复原图坐标后再计 IoU。
GT 与 prediction 使用独立文档／schema：GT 不接收 score/model_id，prediction 不
写入 verified 人工结论，两个 lock 的内容与 digest 分开。

`appearance_group_id` 表示一次独立出现／共同来源的视觉支持组：同一亡灵部署的
三只单位属于一个组；同一单位持续跨帧属于原组；变形／死亡衍生与同一召唤因果链
保留 parent，不能用改 ID 把其计成更多独立出牌。不能确认是否独立的组不计入支持门槛。
这不要求本阶段实现自动跟踪；组与因果来自人工证据，并且保留未确认状态。

### 3.1 普通／觉醒及未知如何训练

taxonomy 描述基类，form 正交储存。首轮只选人工能明确区分且数据够用的普通
视觉类型；不承诺自动觉醒识别。已知 class、未知 form 的对象可保留 class GT，
但不能冒充 normal GT 或作为普通类别 Negative。

为了首轮不添加自定义 owner head，建议将确认的 `(visual_class_id, owner)` 编码为
后端 joint label，canonical 存储仍正交。3–5 基类 × own/opponent 最多 6–10 输出标签。
两种归属都需要明确开发监督；缺少归属支持的类别不假称能识别 opponent。
normal-only 首轮导出仅接受已确认普通形态；未知／其他形态保持 ignore/pending。
Faster R-CNN 背景 ID 0 与 YOLOX 从 0 开始的前景 ID 使用独立、锁定的 backend map。

必须标完整帧内所有入选视觉类型，包括我方、对手及其他 source_card 的同类单位。
未知 owner、未知／其他 form、遮挡无法穷尽的入选对象，不能被遗漏为 background。
若首轮后端不支持可靠 ignore-region loss，**整张图暂不导出训练／计分**，保留原图
和原因；不能只删未知框再当负样本。统计丢弃比例和类别偏差，不因难而排除整场比赛。
未来 form head／更多明确形态需单独扩展实验，不降低此条规则。

### 3.2 外部资料导入与历史兼容

暂不导入任何 reference_only 数据。以后许可明确才建立有版本 import map：
upstream name/id → canonical class/kind/form/owner；默认 side=0 不作为已确认归属。
upstream ROI 裁切坐标必须有完整 offset／scale／旋转才能回到原图；缺失则隔离，不猜。
同一 source video／episode 的 underlying match 不明确，不允许用随机帧划分代替身份。
辅助模型产生的标签需注明 assisted provenance，不伪装成人工盲测 GT。

旧 2A2 六张组合框不能自动拆成逐只框。新标签使用新 ID／派生引用／新的忽略路径；
旧 frame_id、证据、锁与失败结果不动。旧训练契约仍可验证历史材料，但不代表
多类别 readiness；新契约不能通过改旧门槛“继承”Training Dataset Lock。

## 4. 新最小 PoC（已接受设计门槛，未执行）

### 4.1 问题与开发支持

问题：**一个小型多类别 detector，能否在从未接触的自然比赛画面里发现多种真实
视觉单位，并区分我方／对手？** 不是“是否恢复完整对手八卡”，不是部署计数器。

- 首轮锁定 **3–5 个 visual classes**，至少两个移动单位类型，可加入一个建筑。
  从按原序复核的自然开发素材选择，不固定亡灵、不因测试表现挑类别。
  必须通过下述 Scale Coverage Gate，不能全部选大而容易识别的目标。
- 初始数据建议至少 **2 场独立开发自然比赛（总体）**。每个入选类至少两个独立
  appearance groups，且 train 与 development_validation 都有可确认的支持；
  每个启用的 `(class, owner)` joint label 在 **train 和 development_validation
  各至少一个人工确认的独立组**，包括每类 own/opponent；仅在 validation 出现
  不算训练支持。若两场无法覆盖，则增加开发素材或报告
  该集合未就绪，不用连续帧补独立组，也不查看未来测试来改集合。
- 每组约 3–5 张有代表性的帧作为人工工作量起点，不是统计独立样本或成功保证。
  报告比赛／组／entity／帧／框五种数量、每类与归属分布、小目标像素尺寸与遮挡。
- 短时法术、投射物、召唤源卡识别暂不作为第一轮通过项目；schema 能表达它们，
  不等于已训练这些类别。之后的扩类另行批准。

这不是把 4 场／8 次换成全产品通用硬指标，而是首次多类别探索的最低支持建议。
少量开发比赛不足以证明普适性；缺口按每类实际支持报告，不请求固定亡灵补录。

### 4.1.1 Scale Coverage Gate — 固定尺度政策，随后选类

首轮集合至少包含 **1 个相对小目标移动单位类 + 1 个中／大目标移动单位类**，
与至少两个移动单位类型的既有要求同时满足；建筑可以补充，但不代替这两个移动代表。
这里的相对尺度来自 Development 实测框，不是按卡名、主观印象、模型置信度或测试表现划分。

固定政策 ID：`dev_moving_area_quantiles_v1`。政策算法在本设计中固定；执行时先冻结
Development 候选全集、whole-match train/validation assignment 与统计快照，再最终选类。
候选全集包括所有满足 4.1 基本独立组与两种归属 train/validation 支持条件的
`kind=unit, mobility=moving, form=normal` 类，不能先选喜欢的 3–5 类再计算分位数。
未合格／不能判定 mobility 的候选也要列出及说明缺口，不能静默删掉困难类。

统计规则如下，均只读取 Development 的人工 GT：

1. 使用旋转校正后的完整原图 `W,H` 与归一化实体框 `w,h`：
   `width_px=w*W, height_px=h*H, short_side_px=min(width_px,height_px), area_norm=w*h`。
   不使用 contact 缩略图、模型 resize、ROI 面积或增强后的尺寸替代原图统计。
2. 框是可见范围。尺度代表框须人工 verified、class/own-or-opponent/normal 均明确，
   并确认 `occlusion=none, truncation=none`，
   避免把遮挡剩余碎片当小单位。每个支持组至少有一张这种明确框的不同真实帧；
   不满足的基本合格候选记录 `scale_support_pending`。它们与所有困难框仍保留，
   不变成 Negative；任何基本合格候选尚不能定尺度时，不冻结最终类别集合。
   尺度代表资格不依赖最终入选类或 3.1 的整帧导出过滤，避免循环选择；
   最终导出可用性及 train/validation 支持须另验，不能用未导出的支持补训练门槛。
3. 同一类／同一组／同一真实帧多个单位的 `area_norm` 先取 median；
   再按组对不同真实帧取 median，按真实比赛对组取 median，最后按类对比赛取 median，
   得到 class score `S`。三只单位、重复导出或多抽同一组帧不会增加独立支持数，
   类尺度不会因为某场或某组图片更多而在候选池中取得更多权重。
   重复导出、裁切／增强不新增统计帧；同场重录与同一因果组不能换 ID 增权。
4. 对全部可定尺度的基本合格移动类的 `S` 等权排序，计算 `Q25,Q75`。
   分位数使用固定线性插值：`k=(N-1)*p, i=floor(k), f=k-i`，
   `Q(p)=(1-f)*S[i]+f*S[min(i+1,N-1)]`，`p=1/4,3/4`。
   用输入十进制值的精确有理数计算；比较前不四舍五入，显示值不作为校验输入。
5. `Q25<Q75` 时，`S<=Q25` 为 `relative_small`；`Q25<S<Q75` 为 `medium`；
   `S>=Q75` 为 `large`。若分位点因 ties 重合但 `min(S)<max(S)`，使用固定 fallback：
   最小 score 为 `relative_small`、最大 score 为 `large`、其余为 `medium`。
   同尺寸必须同组，不按 ID／卡名／名次拆分 ties；fallback 使用与否须写入统计快照。
   `N<2`、全等尺度、尺度支持未完成或入选集合缺少任一必需尺度时，
   Scale Coverage Gate 不通过，输出 **`SIZE_COVERAGE_INSUFFICIENT`**。

报告所有候选及入选类的真实比赛／独立组／真实帧／实体框数量，以及原图分辨率分布、
`width_px / height_px / short_side_px / area_norm` 的 min、P10、P50、P90、max。
同时报告全部已复核框与清晰尺度代表框两套统计、排除原因与数量、class score、cutpoints
和 scale group；清晰支持还按 match/group/owner 分解。最终训练导出另报实际可用尺度
分布，不能反算改写冻结的候选尺度政策；不只报入选类，也不把归一化面积称为固定像素尺寸。
这些是相对开发分布的尺度，不宣称满足 COCO 的绝对小目标定义或已有小目标识别性能。

缺少合格小目标或其他尺度支持时，按原顺序增加／复核自然 Development 素材，
不降低门槛、不恢复专项补亡灵、不移动未知／另一形态去凑负样本。所有历史素材保留。
新素材或纠正统计需新的候选／尺度快照及 freeze version；不能覆盖旧版本。
政策、候选全集、统计、分位边界、类别选择与 split 一起进入 Dataset Lock digest。
未来测试无论 PASS／FAIL，都不能反向更改尺度分组、类集合或本轮门槛。

### 4.2 划分、冻结与未见自然比赛

已留存四份素材都有历史像素／边界暴露，**只能 development/reference，不能 blind test**。
当前 pending、截断疑点与 Unknown 保留；本轮不重看、不修标签、不追问旧专项缺口。
以后采用哪种局部训练素材规则仍需新设计批准；本设计只用已确认完整回放
进入初始开发支持，不把不完整文件伪装整局。无结算 UI 合法，实际首末边界规则保留。

建议先按 underlying match 冻结 train/development_validation。目标类别、整数映射、
输入尺寸、ROI、缩放、NMS、训练代码／权重、参数和 confidence threshold 只能由
开发数据确定；完整战场，不用上半场代替 owner。随后冻结新的 Model Lock（未来授权）。

**预注册接下来的前两场全新自然完整比赛作为探索性测试 cohort**，按取得顺序，
不要求看见某卡才选局，不安排对手，所有比赛均保留。每局人工 GT 在任何模型预测
之前锁定；标注者未见预测。它们与所有开发／校验素材的 underlying match 不同。
旧单卡“首场含亡灵”选择规则仅属历史协议，不套用新 multiclass cohort。

两局合计至少出现三个锁定的 **opponent** 视觉类，其中至少两个移动单位类；
每个锁定类都有 opponent GT，且每局至少两个锁定的 opponent 类共同出现。
cohort 还至少需要一个锁定类的 own GT，作为归属区分对照；不强求每类两种归属
都在这两局出现，但缺失的 own 子组必须报告未评估，不能宣称该组已通过。
如果没有这些覆盖，输出 `COVERAGE_INSUFFICIENT`，不删无目标局、不临时缩小类别集、
不挑第三场替换。追加测试需新批准且报告累计结果，失败不能自动调参重试。

### 4.3 评价边界与建议 stop rule

首轮人工框工作量限制：在完整战斗区间按预先固定 **1 FPS 请求点**使用现有实际
PTS 抽帧语义，逐帧穷尽标注入选类及归属。重复真实帧仅计一次；miss／无法判定
帧明确排除并报告；排除规则在预测前固定，不按结果删帧。
额外部署关键帧只作补充观察，不混入均匀样本主指标。此采样可能漏掉短时现象，
所以不用于首轮法术评价或部署延迟评价。

主指标：固定采样且可评估帧上的每类 box TP/FP/FN、precision/recall，macro 汇总，
owner 混淆、尺度／遮挡分层；TP 要求一对一配对、正确 visual class 与 owner、
IoU >=0.5。重复框为 FP，不因数量多而算更高部署命中。分数阈值开发期选定后锁定。
所有其他已锁定类与测试帧都保留；未入选类别不被宣称已会识别，误判为入选类会产生 FP。

建议 `EXPLORATORY_MULTICLASS_PASS`：覆盖条件满足，且每个可评估的
`(visual_class, owner)` 子组至少一个 TP、precision 与 recall 均 >=0.70；
**有 GT 或有预测即为可评估**。
**所有锁定类的 opponent 子组均须通过**；出现的 own 子组同样单独验收。
任一可评估子组不达标为 INSUFFICIENT；必需覆盖无支持／无可评估标注为
COVERAGE_INSUFFICIENT，不把 0/0 算 100%。归属错判计入相应子组 FP/FN；
无 GT 子组若产生预测，precision 为 0 并计 FP，明确触发 INSUFFICIENT，
而不是以“无 GT”忽略误报。
无 GT 且无预测的非必需 own 子组只报告未评估。
同时披露 visual-class 聚合与 owner 混淆，不用聚合 own 成功掩盖 opponent 失败。
低样本结果只证明探索性可行，不是可靠性认证。

**本 PoC 不报告 FP/min 或 2 秒出牌延迟**：抽样图片不能认证完整时间轴；负截图不
是时间分母。以后若评估事件级 FP/min，必须另外人工复核连续存在／缺席／Unknown
区间、定义检测到事件的转换与时间口径；Unknown／另一形态不能用于该分母。
达到探索性 PASS 也不自动批准 Module 3、手机实时使用或绝不封号。

## 5. 新 Dataset Lock 的实验语义

canonical SHA-256 覆盖：schema/taxonomy 版本与类别定义；owner/form/ignore
策略；backend label map；源身份与许可用途依据；原图／PTS／标注绑定；group／
因果关系；coverage；whole-match split assignment；所有数据选择／排除及变换参数；
Scale Coverage 政策、候选全集／统计／cutpoints、入选类别与尺度 gate 结果。
稳定排序和显式时间字段使同语义 digest deterministic；变更创建新 freeze version，
exclusive creation，不覆盖任何旧锁。模型与测试 GT 分别锁定，GT 不储存 prediction。
哈希不能证明人为 attestation、授权真实性或源视频从未被一致伪造。

## 6. 实施建议与授权停点

以下是设计要求对应的授权分段；新[实施计划](../plans/2026-10-05-module-2b2b-multiclass-data-training-infrastructure.md)
需要独立复核／批准，本轮不执行该计划：

1. 新 closed schema、独立 readiness、Scale Coverage Gate、历史兼容与纯合成测试；
   不安装模型，reference_only 素材不导入。
2. 逐任务扩展现有标注／绑定工具与多类别导出；精确检验 unknown/background、
   source-card 多对多、组去重、backend IDs 和整场隔离；数据不足就停。
3. 在明确素材用途后，按原顺序做人工多类别数据准备和不可覆盖的 Multi-class
   Dataset Lock；不覆盖旧 2A2 Development Lock，不重新跑 2B-1。
4. **另行授权**模型环境资格验证：新隔离环境、框架／代码许可和实际 CUDA／4GB
   合成 smoke test；无预训练权重、无真实训练。先 Nano，不能自动升级 Tiny／Faster。
   预训练权重来源／许可证／SHA 审查和下载仍需下一次独立授权，不升级现有环境。
5. **再另行授权**训练／开发评价、Model Lock、未见比赛 GT Lock 与首次盲测；
   ONNX/ncnn parity 是另一个验证步骤，手机部署留在后续模块。

本设计阶段在记录用户报告的独立验收、补充尺度要求并完成文档检查后收尾。
下一步仅交付 Module 2B-2B 实施计划供复核；设计验收不自动授权数据准备、
环境安装、训练、Model Lock、盲测或上述任何执行步骤。

## 7. 复核清单

- 公开的 155 标签不等于 155 卡，过时／UI／派生对象明确；资料权利未被根 LICENSE 洗白。
- 卡牌映射与事件身份可为空；召唤／变形不会被新 visual class 直接变成新出牌。
- owner/form 独立，Unknown／其他 form 不作为普通类 Negative；后端 ignore 不可用时不偷删框。
- 旧实现／锁／失败证据完整保留；新门槛是已接受设计，不假称已实现多类别 validator。
- 尺度政策先固定、Development 候选全集先统计再选类；大小 ties 不按卡名拆分。
- 至少一个相对小移动类和一个中／大移动类；不足报告 SIZE_COVERAGE_INSUFFICIENT。
- split 以真实比赛隔离，旧四份不作盲测；两场 prospective cohort 不按结果替换。
- 新门槛评估多类真实单位／owner，不继续专项亡灵补齐；稀疏帧不宣称 FP/min。
- GPU／手机性能、训练与识别成功均未验证；所有实施与新模型素材仍受后续授权控制。
