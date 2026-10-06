# Module 2B-2B — Multiclass PoC Data & Training Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可信的多类别开发数据与不可覆盖锁，并将模型环境资格验证隔离为另行授权的阶段，不直接训练。

**Architecture:** 在现有 Python 工具中增加独立多类别契约、尺度／数据 readiness、受检媒体绑定、手工标注与后端导出入口。复用既有公共安全解析、原图／PTS 校验和坐标工具，不复用固定亡灵门槛或修改旧锁。Phase A 数据验收与 Phase B 环境资格各有停止点。

**Tech Stack:** Phase A：现有 Python 3.12、标准库、PyAV、Pillow、pytest、Tk；不加依赖。Phase B：先审查版本／许可／GPU 驱动及 CUDA 兼容性，再在独立环境资格验证 YOLOX Nano；不下载权重、不用真实训练数据。

**Spec:** [已接受并补充尺度门槛的 2B-2A 设计](../specs/2026-10-05-module-2b2a-multiclass-design.md)；[固定来源／模型比较](../../research/2026-10-05-multiclass-dataset-taxonomy-audit.md)。

Status: **PHASE_A_AUTHORIZED_WITH_SIMPLIFICATION — Task 1–6 only**，2026-10-05。
用户报告 ChatGPT 独立复核并正式授权 Phase A；owner support 以以下最终规则为准。
Task 7 / Phase B、依赖安装、权重下载、训练和推送／合并均不授权。
规划基准：本地 `cec8abc35fce2438d149fe4b68b203650cb835e4` 加本轮文档修订。
执行前必须重新核对批准后的 HEAD，而不是盲用此历史 SHA 或丢弃尚未进 main 的旧数据工具。

## Global Constraints

- 首轮 3–5 个 visual classes，至少两个移动单位类；至少一个 relative_small 移动类与一个 medium/large 移动类。
- 至少两场独立自然 Development 比赛；每个入选类的 opponent 在 TRAIN 与 DEV_VAL 各至少一个确认独立 appearance group；整个集合至少一个入选类另有 own 在两个 split 的独立支持。其余类 own 缺口报告 not_qualified / not_evaluated，不阻止 opponent PoC 或宣称双向区分。Unknown owner 不变为 opponent/Negative；图片／实体数不代替组／比赛数。
- `dev_moving_area_quantiles_v1` 在选类前固定；全部基本合格移动候选的 Development GT 统计先冻结，不能按卡名或未来测试表现分组。
- Unknown／另一形态不是 Negative；后端无可靠 ignore loss 时，存在入选未知对象的整帧 pending，不删框后当背景。尺度统计不依赖这个选类后的过滤。
- 完整回放采用用户确认＋实际 `0..last_frame_seconds`，无结算 UI 合法；技术错误、明确截断／缺失或人工不完整仍拒绝。
- 全部既有四份暴露过的素材只能 development/reference；新的 blind test、Model Lock、Test GT 与推理均不在本计划执行范围。
- reference_only 素材／权重不得导入；自录不等于资产权利清除，训练用途需记录可审查依据。无依据报告 PROVENANCE_INSUFFICIENT，不编造许可。
- 普通亡灵不再专项补齐；旧 schema／4场8次历史行为、2A2 锁、2B-1 FAIL 与所有原始私人文件不修改／删除／覆盖。
- Phase A 不装 torch/torchvision、模型代码或权重；Phase B 另行批准。无训练 epochs、optimizer step、阈值选择、模型路线自动切换、Module 3、Android／实时／游戏输入。
- 不更换现有环境。所有媒体／标签／报告／锁写新 Git-ignored 路径；源代码和脱敏合成 fixtures 才进 Git。当前没有 push、merge、PR、Release 授权。

## Review Focus

1. 同场重录、连续帧、三只群体单位／同因果召唤改 ID 不能增加独立支持或跨 split：Task 1/2 的 identity 与分组测试。
2. 清晰框不足、并列分位数、同图重复导出、原分辨率变化不能人为凑尺度覆盖：Task 2 的 fixed-policy／dedup／tie／pixel-stat 测试。
3. 先挑类／修改统计再冻结，或用最终导出过滤反改候选分组：Task 2/3 的全候选快照、选择绑定、digest 重算测试。
4. 未知归属／形态、漏标对象、Faster 背景 0 与 YOLOX 前景 0 混淆：Task 4/5 的整帧 pending 与映射测试。
5. 媒体被换、坏报告、越界路径、重复 freeze／写到一半失败不能接受或损坏旧锁：Task 3/5 的磁盘重读、独占／保护和 path-free CLI 测试。

---

## 0. 执行合同与阶段门

本轮用户已批准 **Phase A Task 1–6**，沿用已选的分任务实施与独立复核方式：
每任务先失败测试→最小实现→对应测试／保护检查→实现与规格复核→局部提交，才继续。
执行者先读 AGENTS/PROJECT/CURRENT_STATE/DECISIONS/此 spec/此 plan，检查 Git 与固定环境。
从批准后的真实文档 HEAD 创建 `codex/module-2b2b-multiclass-infrastructure`；不直接从
旧 main 开始以丢掉未合并的 data 工具，不切换或清理含用户改动的目录。

Phase A 的 Task 1–6 可以按批准范围依次执行；Task 6 到 MULTICLASS_DATASET_LOCKED
或数据／尺度／来源不足就停止。用户独立验收 A **不等于**允许 Task 7 的安装／GPU 工作。
Phase B 的 Task 7 需要另外授权；完成 ENV_QUALIFIED 或 ENV_INSUFFICIENT 再停。
真实训练、权重下载、Model Lock 和未见测试需再写并批准下一计划。

复用不改的公共 API：`load_evidence(Path)`、`EvidenceError`（严格 JSON），
`load_indexes(paths)`（报告／PTS／PNG），`file_hash(path)`、`frame_id(recording_id,raw_pts,time_base)`、
`canonical_bytes(value)`；`private_artifact_path(Path)`／`dataset_artifact_path(data_root,relative)`
（真实 Git ignore／未跟踪与容器安全）；`canvas_box_to_normalized(box,image_size,display_rect)`。
旧 `bind_dataset/freeze_dataset/grouped_folds/launch_annotator` 均固定 Minions v1，不能作为新门槛。
旧 canonical JSON 保留数组顺序，新层须先按语义 ID 排序集合，但 **intake 原序必须保留**。

## 1. 新文件责任与接口类型

所有下列源码／测试均在 `tools/offline_video/`，不修改旧源码或 requirements。

| 新文件（src/clash_tracker_video/ 下） | 职责 |
|---|---|
| multiclass_contract.py | closed v1 GT/schema/identity/split 校验、下面的 TypedDict 类型 |
| multiclass_readiness.py | 基本候选资格、尺度统计／覆盖、最终导出支持 readiness |
| multiclass_dataset.py | 安全媒体／标签绑定、候选尺度快照和 Dataset Lock 的独占写入／加载 |
| multiclass_annotation.py | 独立手工多类／owner/form UI 和新 revision 保存 |
| multiclass_export.py | 后端映射／标注导出／原图变换与可用性，无模型 import |
| multiclass_cli.py | 独立入口及退出码，无旧 CLI 改动 |
| model_environment.py | Phase B 独立环境子进程合成资格探针；Phase A 不创建 |

对应测试文件 `tests/test_<module>.py`，共七份；合成 fixture 集中在
`tests/multiclass_fixtures.py`，只用假比赛与程序生成图像，无真实路径／媒体。
未来实现文档：`docs/MODULE_2B2B_CONTRACTS.md`、`docs/VERIFICATION_M2B2B.md`；
每任务仅同步这些文档及 CURRENT_STATE，阶段验收才更新 README/DEVELOPMENT_PLAN。

统一类型在 `multiclass_contract.py` 定义（均为 JSON-compatible closed TypedDict，非任意动态字段）：

- `MulticlassDraft` 根：kind=`multiclass_visual_dataset`、schema_version=1、dataset_id、freeze_version、created_at、taxonomy、coordinate_policy、intake、matches、recordings、groups、frames、annotations、annotation_sources、coverage、provenance、split_assignment、selection、backend_label_maps。
- 行结构由 spec §3 决定：taxonomy 的 mobility=moving/static/unknown；group 带 causal_root_id、可空 parent/entity/human_deployment、independence attestation；frame 绑定 PTS／原图，coverage 包含 class 集合／穷尽状态／unknown/ignore；GT 禁 score/model_id。
- recording 行保留技术／完整性／人工观看声明与原图/PTS元数据，新增闭合 `match_segment={start_seconds,end_seconds,complete_match}`；user_confirmed 的完整开发段必须恰为0..last_frame_seconds。split值固定为 train/development_validation，prospective_test仅留作未来身份拒绝检查，不允许进入开发资格／尺度统计。
- `selection` 草稿可为空；非空时闭合为 selected_class_ids、每类选择／未选原因、scale_snapshot_digest、policy_id；IDs 不硬编码卡名。backend_label_maps 在无selection时为空，选类后必须是闭合的 yolox/torchvision 两份映射。kind/type/owner/form/因果/时间字段的枚举与可空语义必须写完整契约，不容许未知键。
- `CandidateReport`：合格 class IDs、每类每 owner/split 的去重 match/group/frame/box 支持、未合格原因；不读取 selection，不以 group ID 数量替代人工独立因果组。
- `ScaleReport`：policy_id、candidate IDs、统计／缺口、精确 score/cutpoints（numerator/denominator）、tie_fallback_used、scale groups、size_coverage_status；包含候选数据／split 的语义 digest。
- `ReadinessReport`：status、ready、blocking_reasons、candidate_report、scale_report、每个入选 joint label 的最终可导出支持；ready=false 不等于坏 schema。
- `BoundMulticlass`：重新加载 draft、checked-media/label snapshots、原始文件 SHA 与 canonical semantic SHA；绑定磁盘上下文，不接受调用者伪造普通 dict。
- `ScaleSnapshot`／`MulticlassLock`：闭合 envelope 的 kind/version/id/created_at/payload/digest。前者冻结未选类候选／split／统计，后者绑定前者、selected classes、backend maps、GT 与实际媒体；彼此独立，不引用旧单卡锁作资格证明。
- `ExportManifest`：dataset_digest、backend、locked joint map、逐帧 transform／原图 hash／label hash、pending/excluded 原因与统计；不存在 prediction 字段。

## Phase A — 数据基础设施、准备与冻结（已批准 Task 1–6）

### Task 1: Closed taxonomy/GT 与真实比赛隔离

**Files:** Create `multiclass_contract.py`、`tests/multiclass_fixtures.py`、`tests/test_multiclass_contract.py`；建立 contracts 文档。

**Interfaces:** `validate_multiclass_shape(draft: MulticlassDraft) -> None`；
`validate_match_splits(draft: MulticlassDraft) -> None`；
`backend_label_maps(selected_class_ids: list[str]) -> dict[str, dict[str, int]]`；上述 TypedDict 类型。
joint map 的键为 `visual_class_id::owner`（class ID 禁止含 `::`），按(class,owner)稳定排序；
own/opponent 两种归属，YOLOX 前景从0、TorchVision前景从1，背景0不写作视觉类。
仅纯结构／语义校验，不能声称验证磁盘真实性或自动确认 human deployment。

- [ ] 写失败测试（合成 fixture）：
  `test_same_match_rerecording_cannot_cross_splits` 将同 match 两份 recording 分 TRAIN/DEV_VAL，`pytest.raises(EvidenceError)`；
  `test_gt_rejects_prediction_fields` 加 score/model_id 必须拒绝；
  `test_unknown_form_does_not_become_normal` 保留 unknown；
  `test_user_confirmed_bounds_without_result_ui` 接受完整 0..last、false result UI，提前结束／迟于0拒绝。
- [ ] 运行 `python -m pytest tools/offline_video/tests/test_multiclass_contract.py -q --tb=short`（本文 `python` 均为 `.\.venv\Scripts\python.exe` 的项目解释器，下方给出标准写法），确认缺接口或规则的真实失败。
- [ ] 实现闭合行／根类型及关系：引用完整、ID 唯一、因果 parent 无环、同 match 派生继承 split，同frame/entity的重复GT拒绝；重复帧／同 group/cause 不能改 ID 制造支持，跨类 source_card 多对多允许 null；不新增固定卡牌列表。
- [ ] 测试 above 全 PASS；另测负面积／越界／bool 冒充整数／NaN／假 mobility／非法 owner／闭合 extra fields及selection/map不一致。运行旧 contract regression，无旧语义差异。
- [ ] 检查仅本任务源码／合成测试／文档 diff，私人保护 PASS，独立复核后提交 `feat(multiclass): add closed visual dataset contract`。

### Task 2: 候选资格、固定尺度政策与独立 readiness

**Files:** Create `multiclass_readiness.py`、`tests/test_multiclass_readiness.py`；补 contracts 文档。

**Interfaces:** consumes Task1 types/validator；produces
`candidate_eligibility(draft: MulticlassDraft) -> CandidateReport`、
`development_scale_report(draft: MulticlassDraft) -> ScaleReport`、
`multiclass_readiness(draft: MulticlassDraft, scale_snapshot: ScaleSnapshot | None = None) -> ReadinessReport`。

- [ ] 写失败测试：
  `test_three_units_and_many_frames_are_one_group`: 三只×5帧仍一组，不足独立支持；
  `test_small_missing_clean_support_is_insufficient`: 基本合格小类全被遮挡，保留该候选且 status=SIZE_COVERAGE_INSUFFICIENT；
  `test_all_equal_scales_fail_coverage`: 不按ID拆 small/large；
  `test_collapsed_quantiles_use_fixed_tie_fallback`: scores=[0.01,0.02,0.02,0.02,0.02] 最小small、其余large，不按ID细分；
  `test_original_resolution_changes_pixels_not_normalized_area`: 两倍W/H像素尺寸两倍、归一化面积不变；
  `test_selected_class_filter_cannot_change_scale_pool`: selection 改变不改变候选 stats/cutpoints。
- [ ] 对新 test file 运行失败周期，记录 FAIL，不拿已通过的兼容测试造假。
- [ ] 实现 spec §4.1.1 的精确有理数、去重与 frame→group→match→class medians、固定 Type7／tie fallback。基本候选从全部预选 GT 支持产生；不读取模型／Test／selection／最终导出过滤。统计所有 reviewed 框与 clean 代表框、owner/split/分辨率／未合格原因。
- [ ] 最终 readiness 独立重算入选3–5类、≥2moving、双尺度：每类 opponent 在 TRAIN/DEV_VAL 有可导出独立支持，集合至少一类 own 在两 split 同时有支持；其余 own 子组报告 not_qualified / not_evaluated。若整帧 pending 清除了必需支持则不就绪，不能拿尺度统计中的未导出帧顶替。无 qualified small 必报 SIZE_COVERAGE_INSUFFICIENT；数据／来源同时不足列出全部原因，不用尺寸成功掩盖其他 gate。补测 opponent-only 多数类可通过、有一类完整 own 通过、无任一完整 own 则不足、Unknown owner 永不补 opponent。
- [ ] 新测试 PASS，并测重复导出不增样本、同场重录不增match、同因果链不增group、未确认 owner/form 排除且保留、prospective_test数据禁止参与尺度、width/height/P10/P50/P90精确示例、政策未知版本拒绝。`ready=true` 仅表示数据资格，旧 review 永远 experiment_gate=false。
- [ ] 私人保护、旧 contract/readiness regression、独立复核 PASS 后提交 `feat(multiclass): enforce development scale coverage readiness`。

### Task 3: 磁盘绑定、先尺度快照后 Dataset Freeze

**Files:** Create `multiclass_dataset.py`、`tests/test_multiclass_dataset.py`；补 contracts 文档。

**Interfaces:** `bind_multiclass(draft: MulticlassDraft, data_root: Path) -> BoundMulticlass`；
`freeze_scale_snapshot(bound: BoundMulticlass, directory: Path) -> ScaleSnapshot`；
`load_scale_snapshot(path: Path, data_root: Path) -> ScaleSnapshot`；
`freeze_multiclass_dataset(bound: BoundMulticlass, scale_snapshot: ScaleSnapshot, directory: Path) -> MulticlassLock`；
`load_multiclass_dataset_lock(path: Path, data_root: Path) -> MulticlassLock`。

- [ ] 写失败测试：`test_freeze_requires_prior_full_candidate_snapshot`（无／伪造 snapshot拒绝），
  `test_selection_cannot_omit_qualified_small_from_inventory`（统计池删除基本合格小候选拒绝），
  `test_frame_swapped_after_bind_is_rejected`（bind后换PNG拒绝），
  `test_same_version_different_digest_cannot_overwrite`（两个并发／不同digest同版本，一个成功且旧锁不变），
  `test_split_and_scale_policy_are_digest_bound`（任一改变必须校验失败／生成不同digest）。
- [ ] 新 test file FAIL 后实现安全 re-read：显式相对 artifacts→既有受检 index/report/PNG＋原视频元数据／hash＋人工sidecar；普通 snapshot 不绕过磁盘加载，freeze/load 重新验证全部依赖与 shape/readiness。
- [ ] 新 canonical 集合按 stable semantic key 排序（intake原序不可排序掉）；区分原始字节hash和语义digest。ScaleSnapshot 冻结无selection且空backend maps的全集/GT统计依据/split；最终 selection引用它，DatasetLock允许只新增selection和Task1固定计算的backend maps，任何GT/split/统计修改需新快照／version。
- [ ] 独占创建：新多类别目录、版本唯一、`xb`/O_EXCL 防竞态；部分写入失败仅清理本操作新文件，不能删除旧锁或用覆盖“修复”。现有 legacy freeze工厂不得扩kind。
- [ ] 新测试 PASS；覆盖乱序等语义digest稳定、intake改序digest变、标签／报告／raw PTS变拒绝、浮点末帧兼容、URL/UNC/traversal/symlink/junction拒绝、reference_only拒绝、没有select先freeze不误称DATASET_LOCKED。复核／保护PASS后提交 `feat(multiclass): add checked immutable dataset locks`。

### Task 4: 人工多类别标注，不自动 Ground Truth

**Files:** Create `multiclass_annotation.py`、`tests/test_multiclass_annotation.py`；复用旧坐标公共函数不改旧 UI。

**Interfaces:** `save_multiclass_revision(draft: MulticlassDraft, *, data_root: Path, output: Path) -> Path`；
`launch_multiclass_annotator(draft_path: Path, *, data_root: Path, output_directory: Path) -> None`。

- [ ] 写失败测试：`test_unknown_object_prevents_exhaustive_export`（保存unknown后frame仍pending），
  `test_invalid_save_does_not_advance_navigation`（坏框保存失败仍在当前帧），
  `test_class_owner_form_are_independent_controls`（改class不重置owner/form为默认normal/opponent），
  `test_group_units_save_without_inventing_new_deployment`（多实体框同group，human_deployment可null）。
- [ ] FAIL后实现原图等比显示、逐只框／class/owner/form/遮挡／group/已穷尽复核；可前后导航，未保存离开提示，不自动确认 unknown／独立因果；保存为新revision配对draft/labels，不覆盖源文件。
- [ ] 新测试PASS；另测画布留白／旋转/缩放边界、sidecar失败时完整旧文件保留；真实GUI测试只用合成图、fresh-process Tk，不跳过／隐藏native GUI错误。
- [ ] `python -m pytest tools/offline_video/tests/test_multiclass_annotation.py tools/offline_video/tests/test_unit_annotation.py -q --tb=short -rs` 无新错误，保护／独立复核PASS；提交 `feat(multiclass): add manual visual annotation revisions`。

### Task 5: 后端标签导出与独立 CLI（无 torch/YOLO import）

**Files:** Create `multiclass_export.py`、`multiclass_cli.py`、`tests/test_multiclass_export.py`、`tests/test_multiclass_cli.py`。

**Interfaces:** `build_backend_label_map(selected_class_ids: list[str], backend: str) -> dict[str, int]`；
`export_multiclass_dataset(lock_path: Path, *, data_root: Path, backend: str, output_directory: Path) -> ExportManifest`；
`main(argv: list[str] | None = None) -> int`（`python -m clash_tracker_video.multiclass_cli`）。
后端仅 `yolox` 与 `torchvision`；两个后端都输出同一已冻结 joint map 的可复现不同整数映射。
build函数复用Task1的 `backend_label_maps`，不另写一套排序／整数规则。

- [ ] 写失败测试：`test_yolox_zero_is_foreground_torchvision_zero_is_background`，
  `test_unknown_other_form_blocks_whole_frame_export`（整个帧不导出而非删框），
  `test_cli_bad_report_returns_two_without_private_paths_or_output`，
  `test_old_review_never_becomes_experiment_ready`，
  `test_pending_support_cannot_satisfy_exported_label_gate`。
- [ ] FAIL后实现 lock受检加载、YOLOX COCO-style JSON／TorchVision通用box-label JSON及只含元数据的manifest；仅写标签、原图引用和可逆geometry metadata，不生成预测、不装模型、不硬编码COCO类别，不把background作新视觉类。
- [ ] 固定类别映射sorted(class,owner)；YOLOX前景从0，TorchVision前景从1；变换保留原图→ROI→输入与逆变换，训练尺寸未获批准时仅identity导出，不猜最终resize/NMS参数。模型具体输入资格留PhaseB；后续需新的artifact/config版本，不能反改旧DatasetLock。
- [ ] CLI子命令：`validate-dataset`／`scale-report`／`freeze-scale`／`freeze-dataset`／`validate-dataset-lock`／`annotate`／`export`。只读有效且ready=0，不足=3，坏输入=2；freeze/export不满足gate=2且不创建成功锁/manifest。路径错误不泄露私人路径。
- [ ] 新测试PASS，另测neutral等未启用归属对象不能被偷删为background；完整旧prepare/validate/review/extractor regressions、fresh GUI与依赖／保护检查PASS；独立复核后提交 `feat(multiclass): expose checked dataset preparation commands`。

### Task 6: 原序 Development 人工准备 → 数据阶段验收停止

**Files:** 只新增 Git-ignored `outputs/module2b2b/data/<new-run-id>/` 的draft/labels/快照/锁与报告；更新 VERIFICATION_M2B2B/CURRENT_STATE。无需改历史private文件。

**Interfaces:** 使用 Task1–5，无 detector/model/旧GT自动迁移。输入仍是原始 intake 顺序；新自然素材按到达顺序追加。

- [ ] 先对批准执行前的全部既有私人文件创建只读 SHA-256 清单并检查Git ignore；记录原录像/2A2锁/2B-1结果，清单自身放新忽略路径，不进公开文档。
- [ ] 技术＋人工原序复核；使用已有定位参考但旧group框不自动拆成单体框。源2的具体截断疑点仍先核实，不因无结算页拒绝，不因找容易卡跳过。不能推断来源／自然独立比赛／形态；必要时只问缺失事实。
- [ ] 人工建立候选taxonomy及逐实体框／因果分组／owner/form/exhaustive coverage。先整理完整候选清单，按match声明TRAIN/DEV_VAL，再重算全部基本候选的class-owner-split资格；这次分配随尺度快照冻结，不按最终类集合反调split。模型／测试不参与；不足只报告每类独立支持缺口，不沿用亡灵4/8。
- [ ] 运行新 `scale-report`；核对候选全集、原图尺寸与面积分布／clean支持、固定policy/cutpoints；通过后先 `freeze-scale`。人工按原设计的支持次数／区分度／可见时间／遮挡／归属明确度记录选类理由，且3–5类满足两种尺度，不按卡名固定优先级。
- [ ] 执行新 `validate-dataset`（0）→`freeze-dataset`→`validate-dataset-lock`（0）；重复加载／digest重算一致；打印真实比赛/组/entity/帧/框、按joint-label与size的统计、所有Unknown/排除比例，不把这些数量混为一谈。
- [ ] 任一gate不足就输出具体缺口并停：尤其 `SIZE_COVERAGE_INSUFFICIENT` 时增加自然Development支持，不能拿测试／降低门槛／挑困难类为negative。不得为了本任务freeze成功伪造或改旧Evidence；保留所有pending。
- [ ] 完整回归、依赖、diff/links/privacy/protection PASS；全阶段独立代码复核后输出 DATA阶段报告，达到锁则 `MULTICLASS_DATASET_LOCKED`，不足则 DATA/SIZE/PROVENANCE_INSUFFICIENT。提交只含代码/测试/脱敏文档，不提交锁/GT。**停下供 ChatGPT/用户验收，不开始Task7。**

## Phase B — 模型环境资格（A验收后另行授权）

### Task 7: 隔离环境与合成运行资格，不训练／不下载权重

**Files:** 另行批准后 Create `model_environment.py`、`tests/test_model_environment.py`；新增忽略路径下environment-request／qualification receipt；当前计划阶段不创建脚本／环境。

**Interfaces:** `validate_environment_request(request: dict[str, object]) -> None`；
`qualify_model_environment(request: dict[str, object], *, output_directory: Path) -> dict[str, object]`。
request 为closed synthetic-only contract：code revision、框架/wheel具体版本与SHA/官方来源/各license、driver/CUDA/GPU预检、approved isolation path、YOLOX Nano配置（416×416、batch=1、FP32、3–5class×owner）、禁止weights/真实dataset的flags。

- [ ] 先读取已验收数据锁的**脱敏尺度元数据**，不加载训练pixels；复核公开官方版本／wheel／YOLOX代码许可证与依赖矩阵。研究中PyTorch2.14/torchvision0.29/cu126仅历史候选，不当自动安装锁；可用性变化输出request冲突并停，不擅自换框架或版本。
- [ ] 将具体pin／hash／许可证／驱动兼容／隔离路径／安装命令写入新的environment request，用户批准该request后才安装。环境位于 Git-ignored `outputs/module2b2b/environments/<request-id>/`，现有 .venv/requirements 不改；pip命令只针对批准解释器和审过的 requirements，不执行未审下载脚本。
- [ ] 写失败synthetic/mock测试：`test_probe_cannot_download_weights_or_read_dataset`，
  `test_gpu_name_without_working_kernel_is_not_qualified`，
  `test_missing_cuda_nms_op_is_insufficient`，
  `test_probe_error_does_not_upgrade_current_venv`。在当前环境跑mock失败周期后实现资格子进程；父数据模块永不import torch，模型仅在独立子进程显式加载。
- [ ] 无预训练权重创建随机 Nano；实际跑固定 synthetic tensors 的forward/loss/backward（无optimizer step、无epochs、无保存模型）与实际检测算子/NMS，记录CUDA/驱动/GPU compute capability/编译架构、峰值显存、耗时、错误。此单次算子资格不等于真实数据训练或学习成功，不保证训练显存足够。
- [ ] FP32、416、batch1 不通过或CUDA不可用即 ENV_INSUFFICIENT；不自动改尺寸／AMP／升级Tiny／换Faster或CPU训练。1050Ti4GB不能由“显卡名称／wheel有sm60”推断支持sm61，必须实际kernel成功。合成forward/backward/NMS全部成功且峰值allocated/reserved均低于实际VRAM才 ENV_QUALIFIED，并报告剩余margin，不宣称epoch性能已验证。
- [ ] 因未下载权重，此阶段仅审未来weight官方来源／license/provenance状态，不保存weights；ONNX/ncnn/mobile parity不运行。mock／旧回归／隔离环境pip check／保护检查PASS，资格报告独立验收后提交 `feat(multiclass): add isolated synthetic environment qualification`。
- [ ] **停止。** 失败报告环境限制；成功仅资格通过。训练、weights下载、threshold、Model Lock和prospective GT/cohort下一阶段另拟计划，不自动执行。

## 2. 每任务与阶段的实际验证命令

本文所有短写 `python -m pytest ...` 均须实际使用当前项目解释器：

```powershell
.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests/test_multiclass_contract.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q --tb=short -rs
.\.venv\Scripts\python.exe -m pip check
git diff --check
git status --short
```

其余新test文件按Task文件名替换第一行；失败周期必须真实FAIL，新实现后PASS。
完整回归数量由实际输出记录，不复制历史680/2；Windows权限skip与Tk错误单独列出。
pip check预期exit0/No broken requirements，diff check预期无输出/exit0。
文档links本地校验无坏相对目标；源码导入不出现torch/模型网络下载副作用。
所有新private路径实际`git check-ignore`命中、`git ls-files`零私有／二进制。
阶段前后既有文件SHA全等；新生成文件不伪装保护原件。GT/locks本地验证只读，hash不证明人类声明真伪。

冻结CLI范例仅在Task5真实实现并用`--help`核实后运行，所有目录全新：

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video.multiclass_cli validate-dataset <draft> --data-root <explicit-root>
.\.venv\Scripts\python.exe -m clash_tracker_video.multiclass_cli freeze-scale <draft> --data-root <explicit-root> --output <new-scale-dir>
.\.venv\Scripts\python.exe -m clash_tracker_video.multiclass_cli freeze-dataset <selected-draft> --scale-snapshot <scale-lock> --data-root <explicit-root> --output <new-lock-dir>
.\.venv\Scripts\python.exe -m clash_tracker_video.multiclass_cli validate-dataset-lock <new-lock> --data-root <explicit-root>
```

尖括号是执行时从明确本地文件清单取值的参数说明，不是现在可以复制执行的命令，
不得猜私人路径。freeze前没有最终selection时validate可合法exit3；选类后最终validate应exit0。
Task 5 实现后的 `--help` 已核对：输入文件是位置参数，尺度锁选项为
`--scale-snapshot`；以上示例仅同步已实现的参数名，不改变阶段或冻结门槛。

## 3. 完成／停点与计划自检

Phase A：schema/identity/Scale gate/annotation/export与旧兼容测试证据＋真实candidate inventory、
尺度快照及dataset lock或缺口报告；Phase B另需实际独立环境receipt。两者都不报告模型成功。
阶段报告列新增/改文件、无DB/migration/cloud变化、真实测试/Not Run、未解决gap、branch/commit/push未授权，停止等待验收。

规划者已对照spec自检：§3 schema/GT/owner/form由Task1/4/5覆盖；§4.1资格及Scale由Task2/3/6；
§4.2/5比赛隔离和版本/digest由Task1/3/6；许可边界由Task3/6/7。§4.3模型评价、Model/Test GT
Lock、未来盲测与移动部署明确不属于本基础设施计划，维持未来授权，不假称已实现。
七个任务的types/signatures相互一致；Review Focus五条各有负责测试，无完整程序正文。
沿用分任务实施与复核，**仅执行已授权 Phase A Task 1–6，到锁定或具体缺口即停止**。
