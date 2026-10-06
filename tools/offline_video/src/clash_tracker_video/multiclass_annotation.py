"""Manual full-image observations and additive checked draft/label revisions.

No prediction, class selection, causal-group creation or negative inference.
Tk is imported only for an explicitly launched local annotation window.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import os
from pathlib import Path
from uuid import uuid4

from .evidence_contract import EvidenceError, load_evidence
from .evidence_prepare import file_hash
from .experiment_lock import MAX_LOCK_BYTES, canonical_bytes
from .multiclass_contract import MulticlassDraft, validate_multiclass_shape
from .multiclass_dataset import bind_multiclass
from .training_dataset import _disk_operation, dataset_artifact_path, private_artifact_path
from .unit_annotation import canvas_box_to_normalized


def _write_new(path, raw, created):
    private_artifact_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
    try:
        info = os.fstat(fd)
        created.append((path, info.st_dev, info.st_ino))
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            if written <= 0:
                raise OSError("Incomplete annotation revision")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)


def _cleanup(created):
    failed = False
    for path, device, inode in reversed(created):
        try:
            info = path.lstat()
            if (not path.is_symlink() and not path.is_junction()
                    and (info.st_dev, info.st_ino) == (device, inode)):
                path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            failed = True
    return failed


def _check_hashes(root, hashes):
    for relative, expected in hashes.items():
        if file_hash(dataset_artifact_path(root, relative)) != expected:
            raise EvidenceError("Original multiclass annotation dependency changed.")


@_disk_operation
def save_multiclass_revision(draft: MulticlassDraft, *, data_root: Path, output: Path) -> Path:
    """Publish a new complete sidecar first, then its checked draft commit point.

An edited draft intentionally differs from old label rows. Old sidecars retain
their declared byte hashes; all media is independently rebound before a new
complete sidecar replaces those references. The pair is not an OS transaction.
Failure removes only files created by this call, never an existing revision.
Every revision invalidates old class selection/backend maps and scale binding.
"""
    created = []
    try:
        validate_multiclass_shape(draft)
        if (not isinstance(data_root, Path) or not data_root.is_absolute()
                or not isinstance(output, Path) or not output.is_absolute() or output.suffix != ".json"):
            raise EvidenceError("Explicit local container and new JSON revision required.")
        destination = dataset_artifact_path(data_root, output.relative_to(data_root).as_posix())
        sidecar = dataset_artifact_path(data_root, destination.with_name(destination.stem + ".labels.json").relative_to(data_root).as_posix())
        if destination.exists() or sidecar.exists():
            raise EvidenceError("Multiclass annotation revision already exists.")
        # Check media without asserting the edited rows equal their previous GT.
        media = deepcopy(draft)
        media["annotations"], media["annotation_sources"] = [], []
        media["selection"], media["backend_label_maps"] = None, {}
        original_hashes = dict(bind_multiclass(media, data_root).file_hashes)
        for source in draft["annotation_sources"]:
            path = dataset_artifact_path(data_root, source["path"])
            # The GUI's first observation has no earlier label artifact. This
            # exact in-memory placeholder can never bind or persist as a lock.
            if (source["annotation_source_id"] == "pending_labels" and source["sha256"] == "0" * 64
                    and path == destination.parent / "pending.labels.json" and not path.exists()):
                continue
            if file_hash(path) != source["sha256"]:
                raise EvidenceError("Original multiclass annotation sidecar changed.")
            load_evidence(path)  # Existing bytes must still be strict JSON.
            original_hashes[source["path"]] = source["sha256"]
        revision = deepcopy(draft)
        revision["selection"], revision["backend_label_maps"] = None, {}
        identity = "labels_" + uuid4().hex
        for annotation in revision["annotations"]:
            annotation["annotation_source_id"] = identity
        labels = {"schema_version": 1, "annotation_source_id": identity,
                  "annotations": deepcopy(revision["annotations"])}
        raw_labels = canonical_bytes(labels) + b"\n"
        revision["annotation_sources"] = [{"annotation_source_id": identity,
            "path": sidecar.relative_to(data_root).as_posix(), "sha256": sha256(raw_labels).hexdigest()}]
        validate_multiclass_shape(revision)
        raw_draft = canonical_bytes(revision) + b"\n"
        if max(len(raw_labels), len(raw_draft)) > MAX_LOCK_BYTES:
            raise EvidenceError("Multiclass annotation revision exceeds strict JSON limit.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        private_artifact_path(destination)
        private_artifact_path(sidecar)
        _write_new(sidecar, raw_labels, created)
        bind_multiclass(revision, data_root)
        _check_hashes(data_root, original_hashes)
        _write_new(destination, raw_draft, created)
        bind_multiclass(load_evidence(destination), data_root)
        _check_hashes(data_root, original_hashes)
        return destination
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, RecursionError) as exc:
        if _cleanup(created):
            raise EvidenceError("Multiclass annotation save failed; new-file cleanup is incomplete.") from exc
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("Cannot exclusively save checked multiclass annotation revision.") from exc


class _MulticlassAnnotator:
    """One manual canvas; rows are visual observations, not new game events."""
    def __init__(self, window, bound, output_directory):
        import tkinter as tk
        from tkinter import ttk
        self.window, self.bound = window, bound
        self.original, self.draft = deepcopy(bound.draft), deepcopy(bound.draft)
        order = {r["recording_id"]: i for i, r in enumerate(self.draft["intake"])}
        # Binding canonicalizes set-like rows for hashing; annotation follows
        # original source intake and each source's actual relative chronology.
        self.draft["frames"].sort(key=lambda r: (order[r["recording_id"]], r["timestamp_seconds"]))
        self.output_directory = output_directory
        self.frame_index, self.dirty, self._loading = 0, False, True
        self.active_annotation_id = None
        self.last_saved_path, self.drag_origin = None, None
        self.window.title("本地多类别人工标注")
        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.canvas = tk.Canvas(window, width=820, height=560, background="#222222", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        controls = ttk.Frame(window, padding=10)
        controls.pack(side="right", fill="y")
        ttk.Label(controls, text="逐个框出可辨识对象。类别、阵营、形态分别人工确认。\n不确定对象用未知区域，不猜类别或新部署。", wraplength=330).pack(anchor="w")
        self.frame_label = ttk.Label(controls, wraplength=330)
        self.frame_label.pack(anchor="w")
        self.units = tk.Listbox(controls, height=5, exportselection=False)
        self.units.pack(fill="x")
        self.units.bind("<<ListboxSelect>>", self._selected)
        self.visual_class = tk.StringVar(value="")
        self.owner, self.form = tk.StringVar(value="unknown"), tk.StringVar(value="unknown")
        self.group, self.entity = tk.StringVar(value=""), tk.StringVar(value="")
        self.occlusion, self.truncation = tk.StringVar(value="unknown"), tk.StringVar(value="unknown")
        self.unit_review = tk.StringVar(value="pending")
        classes = [c["visual_class_id"] for c in self.draft["taxonomy"]["classes"]]
        for title, variable, values in (
            ("视觉类别", self.visual_class, ("", *classes)),
            ("阵营", self.owner, ("own", "opponent", "neutral", "unknown")),
            ("形态", self.form, ("normal", "evolved", "unknown")),
            ("既有 appearance group；可留空", self.group, ("",)),
            ("已人工确认的实体 ID；可留空", self.entity, None),
            ("遮挡", self.occlusion, ("none", "partial", "unknown")),
            ("边缘截断", self.truncation, ("none", "partial", "unknown")),
            ("选中框复核", self.unit_review, ("pending", "verified")),
        ):
            ttk.Label(controls, text=title).pack(anchor="w")
            widget = ttk.Entry(controls, textvariable=variable) if values is None else ttk.Combobox(
                controls, textvariable=variable, values=values, state="readonly")
            widget.pack(fill="x")
            if variable is self.group:
                self.group_control = widget
        self.unknown_object = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="新框为未确定类别的未知区域", variable=self.unknown_object).pack(anchor="w")
        ttk.Button(controls, text="新框模式（先应用当前框编辑）", command=self._new_box).pack(fill="x")
        ttk.Button(controls, text="应用选中框信息", command=self._apply_metadata).pack(fill="x")
        ttk.Button(controls, text="从新草稿移除选中框（原文件保留）", command=self._delete).pack(fill="x")
        self.exhaustive, self.full_review = tk.BooleanVar(value=False), tk.BooleanVar(value=False)
        self.resolve_unknown = tk.BooleanVar(value=False)
        self.reviewer, self.notes = tk.StringVar(value=""), tk.StringVar(value="Manual frame review")
        ttk.Label(controls, text="本帧已穷尽复核的类别（可多选）").pack(anchor="w")
        self.class_coverage = tk.Listbox(controls, height=min(5, len(classes)), selectmode="multiple", exportselection=False)
        for cid in classes:
            self.class_coverage.insert("end", cid)
        self.class_coverage.pack(fill="x")
        ttk.Checkbutton(controls, text="已逐项复核上面选中的类别", variable=self.exhaustive).pack(anchor="w")
        ttk.Checkbutton(controls, text="复核覆盖完整原图", variable=self.full_review).pack(anchor="w")
        ttk.Checkbutton(controls, text="本帧既有未知/忽略内容已人工解决", variable=self.resolve_unknown).pack(anchor="w")
        for title, variable in (("人工复核者", self.reviewer), ("复核说明", self.notes)):
            ttk.Label(controls, text=title).pack(anchor="w")
            ttk.Entry(controls, textvariable=variable).pack(fill="x")
        ttk.Button(controls, text="追加保存新 revision", command=self._save).pack(fill="x")
        nav = ttk.Frame(controls)
        nav.pack(fill="x")
        ttk.Button(nav, text="上一帧", command=self._previous).pack(side="left")
        ttk.Button(nav, text="下一帧", command=self._next).pack(side="right")
        self.status = tk.StringVar(value="保存不等于数据合格；未知内容不会当作负样本。")
        ttk.Label(controls, textvariable=self.status, wraplength=330).pack(anchor="w")
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        self.canvas.bind("<ButtonRelease-1>", self._drag_end)
        self.canvas.bind("<Configure>", self._render)
        for variable in (self.visual_class, self.owner, self.form, self.group, self.entity,
                         self.occlusion, self.truncation, self.unit_review, self.exhaustive,
                         self.full_review, self.resolve_unknown, self.reviewer, self.notes):
            variable.trace_add("write", self._control_edited)
        self.class_coverage.bind("<<ListboxSelect>>", self._control_edited)
        self._show_frame(self._load_image(0))

    def _control_edited(self, *_):
        if not self._loading:
            self.dirty = True

    def _frame(self):
        return self.draft["frames"][self.frame_index]

    def _rows(self):
        return [r for r in self.draft["annotations"] if r["frame_id"] == self._frame()["frame_id"]]

    def _coverage(self):
        fid = self._frame()["frame_id"]
        existing = next((r for r in self.draft["coverage"] if r["frame_id"] == fid), None)
        if existing is None:
            existing = {"coverage_id": "coverage_" + uuid4().hex, "frame_id": fid,
                "recording_id": self._frame()["recording_id"], "exhaustive_for_classes": [],
                "exhaustive_state": "pending", "reviewed_regions": [], "unknown_intervals": [],
                "ignore_regions": [], "ignore_reasons": [],
                "review_provenance": {"method": "pending", "reviewed_by": None, "notes": "Manual review pending"}}
            self.draft["coverage"].append(existing)
        return existing

    def _invalidate(self):
        self.dirty = True
        self.draft["selection"], self.draft["backend_label_maps"] = None, {}
        self._frame()["review_state"] = "pending"
        coverage = self._coverage()
        coverage["exhaustive_state"], coverage["exhaustive_for_classes"] = "pending", []
        self.exhaustive.set(False)
        self.full_review.set(False)
        self.resolve_unknown.set(False)

    def _load_image(self, index):
        from PIL import Image
        frame = self.draft["frames"][index]
        path = dataset_artifact_path(self.bound.data_root, frame["image_path"])
        if file_hash(path) != frame["image_sha256"]:
            raise EvidenceError("Current multiclass annotation image changed.")
        with Image.open(path) as image:
            image.load()
            result = image.convert("RGB")
        if result.size != (frame["image_width"], frame["image_height"]):
            raise EvidenceError("Annotation original image dimensions conflict.")
        return result

    def _show_frame(self, image):
        self._loading = True
        self.active_annotation_id = None
        self.image, self.image_size = image, image.size
        frame, coverage = self._frame(), self._coverage()
        record = next(r for r in self.draft["recordings"] if r["recording_id"] == frame["recording_id"])
        self.group_control.configure(values=("", *[r["appearance_group_id"] for r in self.draft["groups"]
            if r["underlying_match_id"] == record["underlying_match_id"]]))
        self.frame_label.configure(text=f"帧 {self.frame_index + 1}/{len(self.draft['frames'])}: {frame['frame_id']}")
        self.exhaustive.set(coverage["exhaustive_state"] == "complete")
        self.full_review.set(coverage["reviewed_regions"] == [{"x": 0, "y": 0, "width": 1, "height": 1}])
        self.resolve_unknown.set(False)
        self.reviewer.set(coverage["review_provenance"]["reviewed_by"] or "")
        self.notes.set(coverage["review_provenance"]["notes"])
        self.class_coverage.selection_clear(0, "end")
        for position in range(self.class_coverage.size()):
            if self.class_coverage.get(position) in coverage["exhaustive_for_classes"]:
                self.class_coverage.selection_set(position)
        self.group.set("")
        self.entity.set("")
        self.owner.set("unknown")
        self.form.set("unknown")
        self.unit_review.set("pending")
        self._refresh()
        self._render()
        self._loading = False

    def _render(self, _event=None):
        if not hasattr(self, "image"):
            return
        from PIL import ImageTk
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        if width <= 2 or height <= 2:
            width, height = 820, 560
        scale = min(width / self.image_size[0], height / self.image_size[1])
        draw_width, draw_height = self.image_size[0] * scale, self.image_size[1] * scale
        left, top = (width - draw_width) / 2, (height - draw_height) / 2
        self.display_rect = (left, top, draw_width, draw_height)
        self.photo = ImageTk.PhotoImage(self.image.resize((max(1, round(draw_width)), max(1, round(draw_height)))), master=self.window)
        self.canvas.delete("all")
        self.canvas.create_image(left, top, image=self.photo, anchor="nw")
        for row in [*self._rows(), *self._coverage()["ignore_regions"]]:
            box = row["box"]
            x, y = left + box["x"] * draw_width, top + box["y"] * draw_height
            self.canvas.create_rectangle(x, y, x + box["width"] * draw_width, y + box["height"] * draw_height,
                                         outline="#ffad42" if "annotation_id" in row else "#ee55cc", width=2)

    def _refresh(self):
        self.units.delete(0, "end")
        for row in self._rows():
            self.units.insert("end", f"{row['visual_class_id']} / {row['owner']} / {row['observed_form']} / {row['review_state']}")

    def _drag_start(self, event):
        self.drag_origin = (event.x, event.y)

    def _drag_move(self, event):
        if self.drag_origin is not None:
            self._render()
            self.canvas.create_rectangle(*self.drag_origin, event.x, event.y, outline="#ffad42")

    def _drag_end(self, event):
        if self.drag_origin is None:
            return
        start, self.drag_origin = self.drag_origin, None
        try:
            self._check_applied_controls()
            box = dict(zip(("x", "y", "width", "height"), canvas_box_to_normalized(
                (*start, event.x, event.y), self.image_size, self.display_rect)))
            if self.unknown_object.get():
                self._coverage()["ignore_regions"].append({"box": box, "visual_class_ids": [], "reason": "Unresolved unknown object"})
            else:
                cid = self.visual_class.get()
                if cid not in {r["visual_class_id"] for r in self.draft["taxonomy"]["classes"]}:
                    raise EvidenceError("Choose a manual visual class or unresolved unknown region.")
                frame = self._frame()
                if not self.draft["annotation_sources"]:
                    self.draft["annotation_sources"] = [{"annotation_source_id": "pending_labels",
                        "path": (self.output_directory / "pending.labels.json").relative_to(self.bound.data_root).as_posix(), "sha256": "0" * 64}]
                self.draft["annotations"].append({"annotation_id": "observation_" + uuid4().hex,
                    "annotation_source_id": self.draft["annotation_sources"][0]["annotation_source_id"],
                    "recording_id": frame["recording_id"], "frame_id": frame["frame_id"],
                    "appearance_group_id": None, "entity_occurrence_id": None, "visual_class_id": cid,
                    "owner": "unknown", "perspective_ref": frame["perspective_ref"], "observed_form": "unknown",
                    "visual_stage": None, "box": box, "source_card_id": None, "source_card_candidates": [],
                    "mapping_basis": "unknown", "mapping_verification": "pending", "occlusion": "unknown",
                    "truncation": "unknown", "review_state": "pending",
                    "review_provenance": {"method": "pending", "reviewed_by": None, "notes": "Manual observation pending"}})
                self.active_annotation_id = None
            self._invalidate()
            self._refresh()
            if not self.unknown_object.get():
                self.units.selection_set(len(self._rows()) - 1)
                self._selected()
            self.status.set("新框待人工复核；没有创建 deployment 或负样本。")
        except EvidenceError as exc:
            self.status.set(str(exc))
        self._render()

    def _selected(self, _event=None):
        selected = self.units.curselection()
        if not selected:
            return
        row = self._rows()[selected[0]]
        prior = next((r for r in self._rows() if r["annotation_id"] == self.active_annotation_id), None)
        if prior is not None and self._controls_differ(prior):
            # A native selection event arrives after Tk changes the highlight.
            # Restore the active row before loading B could discard A's edits.
            self.units.selection_clear(0, "end")
            self.units.selection_set(self._rows().index(prior))
            self.status.set("请先应用当前框的编辑，再选择另一框；未应用内容仍保留。")
            return
        self.active_annotation_id = row["annotation_id"]
        self._loading = True
        for variable, key in ((self.visual_class, "visual_class_id"), (self.owner, "owner"),
            (self.form, "observed_form"), (self.occlusion, "occlusion"), (self.truncation, "truncation"), (self.unit_review, "review_state")):
            variable.set(row[key])
        self.group.set(row["appearance_group_id"] or "")
        self.entity.set(row["entity_occurrence_id"] or "")
        self._loading = False

    def _apply_metadata(self):
        selection = self.units.curselection()
        if not selection:
            self.status.set("请先选中一个视觉框。")
            return
        row = self._rows()[selection[0]]
        cid = self.visual_class.get()
        if cid != row["visual_class_id"]:
            row.update(source_card_id=None, source_card_candidates=[], mapping_basis="unknown", mapping_verification="pending")
        row.update(visual_class_id=cid, owner=self.owner.get(), observed_form=self.form.get(),
            appearance_group_id=self.group.get() or None, entity_occurrence_id=self.entity.get() or None,
            occlusion=self.occlusion.get(), truncation=self.truncation.get(), review_state=self.unit_review.get())
        reviewer = self.reviewer.get().strip()
        row["review_provenance"] = {"method": "manual" if reviewer and row["review_state"] == "verified" else "pending",
            "reviewed_by": reviewer or None, "notes": self.notes.get().strip() or "Manual observation pending"}
        self._invalidate()
        self._refresh()
        self.units.selection_set(selection[0])
        self.status.set("独立字段已更新；整帧覆盖和旧选择已失效。")

    def _delete(self):
        selected = self.units.curselection()
        if selected:
            self.draft["annotations"].remove(self._rows()[selected[0]])
            self.active_annotation_id = None
            self._invalidate()
            self._refresh()
            self._render()

    def _apply_review(self, draft):
        fid = self._frame()["frame_id"]
        frame = next(r for r in draft["frames"] if r["frame_id"] == fid)
        coverage = next(r for r in draft["coverage"] if r["frame_id"] == fid)
        reviewer = self.reviewer.get().strip()
        reviewed = {"method": "manual" if reviewer else "pending", "reviewed_by": reviewer or None,
                    "notes": self.notes.get().strip() or "Manual frame review"}
        classes = [self.class_coverage.get(i) for i in self.class_coverage.curselection()]
        if self.exhaustive.get() and (not self.full_review.get() or not classes or not reviewer):
            raise EvidenceError("Complete coverage requires explicit classes, full-image review and reviewer.")
        relevant = set(classes)
        uncertain = (bool(coverage["ignore_reasons"])
            or any(not r["visual_class_ids"] or relevant.intersection(r["visual_class_ids"])
                   for r in [*coverage["unknown_intervals"], *coverage["ignore_regions"]])
            or any(r["visual_class_id"] in relevant and (r["owner"] == "unknown" or r["observed_form"] == "unknown")
                   for r in draft["annotations"] if r["frame_id"] == fid))
        if self.resolve_unknown.get():
            if not self.exhaustive.get():
                raise EvidenceError("Resolving unknown content requires explicit complete manual review.")
            coverage.update(unknown_intervals=[], ignore_regions=[], ignore_reasons=[])
            uncertain = any(r["visual_class_id"] in relevant and (r["owner"] == "unknown" or r["observed_form"] == "unknown")
                            for r in draft["annotations"] if r["frame_id"] == fid)
        complete = self.exhaustive.get() and not uncertain
        coverage.update(exhaustive_for_classes=classes, exhaustive_state="complete" if complete else "pending",
            reviewed_regions=[{"x": 0, "y": 0, "width": 1, "height": 1}] if self.full_review.get() else [], review_provenance=deepcopy(reviewed))
        frame["review_state"] = "complete" if complete else "pending"
        frame["review_provenance"] = deepcopy(reviewed)

    def _control_values(self):
        return {"visual_class_id": self.visual_class.get(), "owner": self.owner.get(),
            "observed_form": self.form.get(), "appearance_group_id": self.group.get() or None,
            "entity_occurrence_id": self.entity.get() or None, "occlusion": self.occlusion.get(),
            "truncation": self.truncation.get(), "review_state": self.unit_review.get()}

    def _controls_differ(self, row):
        return any(row[key] != value for key, value in self._control_values().items())

    def _check_applied_controls(self):
        row = next((r for r in self._rows() if r["annotation_id"] == self.active_annotation_id), None)
        if row is not None and self._controls_differ(row):
            raise EvidenceError("Apply the selected observation controls before saving or navigating.")

    def _new_box(self):
        try:
            self._check_applied_controls()
            self.active_annotation_id = None
            self.units.selection_clear(0, "end")
            self._loading = True
            for variable in (self.owner, self.form, self.occlusion, self.truncation):
                variable.set("unknown")
            self.group.set("")
            self.entity.set("")
            self.unit_review.set("pending")
            self._loading = False
            self.status.set("选择新框类别并绘制；阵营、形态和 group 不沿用上一框。")
        except EvidenceError as exc:
            self.status.set(str(exc))

    def _save(self):
        try:
            self._check_applied_controls()
            self._apply_review(self.draft)
            validate_multiclass_shape(self.draft)
            current = bind_multiclass(self.original, self.bound.data_root)
            if current.file_hashes != self.bound.file_hashes:
                raise EvidenceError("Original annotation dependencies changed before save.")
            output = self.output_directory / ("revision_" + uuid4().hex + ".json")
            saved_path = save_multiclass_revision(self.draft, data_root=self.bound.data_root, output=output)
            saved = load_evidence(saved_path)
            checked = bind_multiclass(saved, self.bound.data_root)
            self.bound, self.original, self.draft = checked, deepcopy(saved), deepcopy(saved)
            self.last_saved_path, self.dirty = saved_path, False
            self._show_frame(self._load_image(self.frame_index))
            self.status.set("新 revision 配对保存并核验；未生成 Scale/Dataset Lock。")
            return True
        except (EvidenceError, OSError) as exc:
            self.status.set(str(exc) if isinstance(exc, EvidenceError) else "Cannot check local multiclass annotation revision.")
            return False

    def _navigate(self, offset):
        from tkinter import messagebox
        try:
            self._check_applied_controls()
            candidate = deepcopy(self.draft)
            self._apply_review(candidate)
            validate_multiclass_shape(candidate)
            target = self.frame_index + offset
            if not 0 <= target < len(self.draft["frames"]):
                self.status.set("已到原序边界；未保存编辑仍保留。")
                return
            image = self._load_image(target)  # Do not advance before image success.
            if self.dirty:
                choice = messagebox.askyesnocancel("未保存编辑", "先保存新 revision？选否保留内存编辑后导航，取消留在本帧。", parent=self.window)
                if choice is None or (choice and not self._save()):
                    return
                if choice:
                    candidate = deepcopy(self.draft)
            self.draft, self.frame_index = candidate, target
            self._show_frame(image)
        except (EvidenceError, OSError) as exc:
            self.status.set(str(exc) if isinstance(exc, EvidenceError) else "Cannot open next local annotation image.")

    def _next(self):
        self._navigate(1)

    def _previous(self):
        self._navigate(-1)

    def _close(self):
        from tkinter import messagebox
        if self.dirty:
            choice = messagebox.askyesnocancel("未保存编辑", "关闭前保存新 revision？", parent=self.window)
            if choice is None or (choice and not self._save()):
                return
        self.window.quit()


def launch_multiclass_annotator(draft_path: Path, *, data_root: Path, output_directory: Path) -> None:
    """Read strict declared local bindings before initializing the real window."""
    window = None
    try:
        path = dataset_artifact_path(data_root, draft_path.relative_to(data_root).as_posix())
        folder = dataset_artifact_path(data_root, output_directory.relative_to(data_root).as_posix())
        draft = load_evidence(path)
        bound = bind_multiclass(draft, data_root)
        if not draft["frames"]:
            raise EvidenceError("Multiclass annotation requires existing declared frames.")
        import tkinter as tk
        try:
            window = tk.Tk()
        except tk.TclError as exc:
            raise EvidenceError("Cannot initialize local Tk annotation window.") from exc
        errors = []

        def callback_failure(exception, value, traceback):
            errors.append(value)
            window.quit()

        window.report_callback_exception = callback_failure
        _MulticlassAnnotator(window, bound, folder)
        window.mainloop()
        if errors:
            raise EvidenceError("Local annotation callback failed.") from errors[0]
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("Cannot open checked local multiclass annotator.") from exc
    finally:
        if window is not None:
            window.destroy()
