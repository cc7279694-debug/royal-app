"""Manual original-image unit boxes and additive paired annotation revisions.

Importing this module creates no GUI. A sidecar alone is not frame-review or
dataset-readiness evidence; each save validates the complete updated draft.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from math import nextafter
import os
from pathlib import Path
from uuid import uuid4

from .evidence_contract import EvidenceError, load_evidence, number, valid_type
from .evidence_prepare import file_hash
from .experiment_lock import MAX_LOCK_BYTES, canonical_bytes
from .training_dataset import (dataset_artifact_path, private_artifact_path,
                               load_dataset_indexes, validate_annotation_source)
from .training_dataset_contract import validate_dataset_shape


def canvas_box_to_normalized(box: tuple[float, float, float, float],
                             image_size: tuple[int, int],
                             display_rect: tuple[float, float, float, float]) -> list[float]:
    """Canvas endpoints to visible [x,y,width,height], without outside clipping.

    display_rect is (left, top, width, height), not endpoint coordinates.
    image_size describes the original rotated image, not the display bitmap.
    """
    if (type(box) is not tuple or len(box) != 4 or not all(number(v) for v in box)
            or type(image_size) is not tuple or len(image_size) != 2
            or any(type(v) is not int or v <= 0 for v in image_size)
            or type(display_rect) is not tuple or len(display_rect) != 4
            or not all(number(v) for v in display_rect)):
        raise EvidenceError("Invalid unit-box canvas geometry.")
    left, top, width, height = (Fraction(str(v)) for v in display_rect)
    if left < 0 or top < 0 or width <= 0 or height <= 0:
        raise EvidenceError("Invalid image display rectangle.")
    sx, sy = width / image_size[0], height / image_size[1]
    if abs(sx - sy) > max(sx, sy) / 1000000000:
        raise EvidenceError("Image display must preserve its original aspect ratio.")
    x0, y0, x1, y1 = (Fraction(str(v)) for v in box)
    low_x, high_x = sorted((x0, x1))
    low_y, high_y = sorted((y0, y1))
    if (not left <= low_x < high_x <= left + width
            or not top <= low_y < high_y <= top + height):
        raise EvidenceError("Unit box must have area entirely inside the displayed image.")
    result = [float((low_x - left) / width), float((low_y - top) / height),
              float((high_x - low_x) / width), float((high_y - low_y) / height)]
    # Keep decimal JSON endpoints inside the exact image after float rounding.
    for position, extent in ((0, 2), (1, 3)):
        if Fraction(str(result[position])) + Fraction(str(result[extent])) > 1:
            result[extent] = nextafter(result[extent], 0)
    return result


def save_annotation_revision(document: dict, output: Path) -> Path:
    """Exclusively save a draft plus <stem>.units.json, preserving every original.

    document is an in-memory request {draft, data_root: absolute Path,
    annotation_source_id}, distinct from the closed persisted unit sidecar.
    """
    created = []
    fd = None
    try:
        if type(document) is not dict or set(document) != {"draft", "data_root", "annotation_source_id"}:
            raise EvidenceError("Invalid paired annotation save request.")
        root = document["data_root"]
        if not isinstance(root, Path) or not root.is_absolute():
            raise EvidenceError("Explicit absolute annotation data container required.")
        if not valid_type(document["annotation_source_id"], "id"):
            raise EvidenceError("New annotation source identity required.")
        if not isinstance(output, Path) or not output.is_absolute() or output.suffix != ".json":
            raise EvidenceError("Explicit new draft JSON destination required.")
        destination = dataset_artifact_path(root, output.relative_to(root).as_posix())
        sidecar_path = dataset_artifact_path(root, destination.with_name(destination.stem + ".units.json").relative_to(root).as_posix())
        if destination.exists() or sidecar_path.exists():
            raise EvidenceError("Annotation revision destination already exists.")
        draft = deepcopy(document["draft"])
        validate_dataset_shape(draft)
        source_id = document["annotation_source_id"]
        if source_id in {s["annotation_source_id"] for s in draft["annotation_sources"]}:
            raise EvidenceError("Annotation revision must use a new source identity.")
        for annotation in draft["unit_annotations"]:
            annotation["annotation_source_id"] = source_id
        labels = {"schema_version": 1, "annotation_source_id": source_id,
                  "unit_annotations": deepcopy(draft["unit_annotations"])}
        validate_annotation_source(labels)
        label_bytes = canonical_bytes(labels) + b"\n"
        draft["annotation_sources"] = [{"annotation_source_id": source_id,
                                         "path": sidecar_path.relative_to(root).as_posix(),
                                         "sha256": sha256(label_bytes).hexdigest()}]
        validate_dataset_shape(draft)
        draft_bytes = canonical_bytes(draft) + b"\n"
        if max(len(label_bytes), len(draft_bytes)) > MAX_LOCK_BYTES:
            raise EvidenceError("Annotation revision exceeds strict JSON size limit.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Recheck both ancestors after creation and again before exclusive opens.
        private_artifact_path(destination)
        private_artifact_path(sidecar_path)
        for path, raw in ((sidecar_path, label_bytes), (destination, draft_bytes)):
            private_artifact_path(path)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
            stat = os.fstat(fd)
            created.append((path, stat.st_dev, stat.st_ino))
            offset = 0
            while offset < len(raw):
                written = os.write(fd, raw[offset:])
                if written <= 0:
                    raise OSError("Incomplete annotation revision write")
                offset += written
            os.fsync(fd)
            os.close(fd)
            fd = None
        return destination
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, RecursionError) as exc:
        cleanup_failed = False
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                cleanup_failed = True
            fd = None
        for path, device, inode in reversed(created):
            try:
                stat = path.lstat()
                if not path.is_symlink() and (stat.st_dev, stat.st_ino) == (device, inode):
                    path.unlink()
            except FileNotFoundError:
                continue
            except OSError:
                cleanup_failed = True
        if cleanup_failed:
            raise EvidenceError("Annotation save failed; cleanup of new files is incomplete.") from exc
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("Cannot exclusively save paired local annotation revision.") from exc


class _Annotator:
    """One manual canvas; edits affect a draft copy until an additive save."""
    def __init__(self, window, draft, indexes, output_directory):
        import tkinter as tk
        from tkinter import ttk
        validate_dataset_shape(draft)
        self.window, self.indexes = window, indexes
        self.original = deepcopy(draft)
        self.draft = deepcopy(draft)
        self.output_directory = output_directory
        self.frame_index = 0
        self.unsaved_ids = set()
        self.last_saved_path = None
        self.drag_origin = None
        self.drag_rectangle = None
        self.window.title("本地单单位标注")
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)
        self.canvas = tk.Canvas(window, width=820, height=560, background="#222222", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        controls = ttk.Frame(window, padding=10)
        controls.pack(side="right", fill="y")
        ttk.Label(controls, text="每个框只标一个可辨识单位的可见部分。\n检查全图；同类的我方和其他来源单位也要标。", wraplength=330).pack(anchor="w")
        self.frame_label = ttk.Label(controls, wraplength=330)
        self.frame_label.pack(anchor="w", pady=6)
        self.units = tk.Listbox(controls, height=6, exportselection=False)
        self.units.pack(fill="x")
        self.units.bind("<<ListboxSelect>>", self._unit_selected)
        self.owner = tk.StringVar(value="unknown")
        self.source_card = tk.StringVar(value="unknown")
        self.form = tk.StringVar(value="unknown")
        self.deployment = tk.StringVar(value="")
        self.occlusion = tk.StringVar(value="unknown")
        self.truncation = tk.StringVar(value="unknown")
        self.unit_review = tk.StringVar(value="pending")
        self.frame_review = tk.StringVar(value="pending")
        self.presence = tk.StringVar(value="unknown")
        self.full_review = tk.BooleanVar(value=False)
        self.reviewer = tk.StringVar(value="")
        self.review_notes = tk.StringVar(value="")
        for title, variable, choices in (
            ("阵营", self.owner, ("opponent", "own", "unknown")),
            ("来源卡牌；不确定用 unknown", self.source_card, None),
            ("形态", self.form, ("normal", "evolved", "unknown")),
            ("确认部署；无归属时留空", self.deployment, ("",)),
            ("遮挡", self.occlusion, ("none", "partial", "unknown")),
            ("画面边缘截断", self.truncation, ("none", "partial", "unknown")),
            ("选中单位复核", self.unit_review, ("pending", "verified")),
        ):
            control = self._control(controls, title, variable, choices)
            if variable is self.deployment:
                self.deployment_control = control
                control.bind("<<ComboboxSelected>>", self._deployment_selected)
        ttk.Button(controls, text="应用信息到选中单位", command=self._apply_metadata).pack(fill="x", pady=3)
        ttk.Button(controls, text="删除尚未保存的新框", command=self._delete_unsaved).pack(fill="x")
        self._control(controls, "本帧内容", self.presence, ("positive", "absent", "unknown"))
        self._control(controls, "本帧复核", self.frame_review, ("pending", "complete", "excluded"))
        ttk.Checkbutton(controls, text="已复核全图，全部可辨识同类单位均已标注", variable=self.full_review).pack(anchor="w")
        self._control(controls, "复核人", self.reviewer)
        self._control(controls, "复核说明", self.review_notes)
        ttk.Button(controls, text="追加保存新版本", command=self._save).pack(fill="x", pady=3)
        ttk.Button(controls, text="下一帧", command=self._next).pack(fill="x")
        self.status = tk.StringVar(value="未知内容保持 pending；清空框不会自动成为负样本。")
        ttk.Label(controls, textvariable=self.status, wraplength=330).pack(anchor="w", pady=6)
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<ButtonRelease-1>", self._drag_end)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        self.canvas.bind("<Configure>", self._render)
        self._show_frame()

    @staticmethod
    def _control(parent, title, variable, choices=None):
        from tkinter import ttk
        ttk.Label(parent, text=title).pack(anchor="w")
        widget = (ttk.Entry(parent, textvariable=variable) if choices is None else
                  ttk.Combobox(parent, textvariable=variable, values=choices, state="readonly"))
        widget.pack(fill="x")
        return widget

    def _frame(self):
        return self.draft["frames"][self.frame_index]

    def _rows(self):
        frame = self._frame()
        return [a for a in self.draft["unit_annotations"]
                if (a["recording_id"], a["frame_id"]) == (frame["recording_id"], frame["frame_id"])]

    def _show_frame(self):
        from PIL import Image
        frame = self._frame()
        path = dataset_artifact_path(self.indexes.root, frame["image_path"])
        if file_hash(path) != frame["image_sha256"]:
            raise EvidenceError("Current annotation image has changed.")
        with Image.open(path) as image:
            image.load()
            new_image = image.convert("RGB")
        if new_image.size != (frame["image_width"], frame["image_height"]):
            raise EvidenceError("Current annotation image dimensions conflict.")
        self.image = new_image
        self.image_size = new_image.size
        mid = next(r["underlying_match_id"] for r in self.draft["recordings"] if r["recording_id"] == frame["recording_id"])
        self.deployment_rows = {d["deployment_id"]: d for d in self.draft["deployments"] if d["underlying_match_id"] == mid}
        self.deployment_control.configure(values=("", *self.deployment_rows))
        self.frame_label.configure(text=f"帧 {self.frame_index + 1}/{len(self.draft['frames'])}: {frame['frame_id']}")
        self.frame_review.set(frame["review_status"])
        self.presence.set(frame["minion_presence"])
        self.full_review.set(frame["all_identifiable_units_labelled"])
        self.reviewer.set(frame["review_provenance"]["reviewed_by"] or "")
        self.review_notes.set(frame["review_provenance"]["notes"])
        self._refresh_units()
        self._render()

    def _render(self, _event=None):
        if not hasattr(self, "image"):
            return
        from PIL import ImageTk
        width = max(2, self.canvas.winfo_width())
        height = max(2, self.canvas.winfo_height())
        if width <= 2 or height <= 2:
            width, height = 820, 560
        scale = min(width / self.image_size[0], height / self.image_size[1])
        draw_width, draw_height = self.image_size[0] * scale, self.image_size[1] * scale
        left, top = (width - draw_width) / 2, (height - draw_height) / 2
        self.display_rect = (left, top, draw_width, draw_height)
        bitmap = self.image.resize((max(1, round(draw_width)), max(1, round(draw_height))))
        self.photo = ImageTk.PhotoImage(bitmap, master=self.window)
        self.canvas.delete("all")
        self.canvas.create_image(left, top, image=self.photo, anchor="nw")
        for row in self._rows():
            box = row["normalized_bbox"]
            x, y = left + box["x"] * draw_width, top + box["y"] * draw_height
            self.canvas.create_rectangle(x, y, x + box["width"] * draw_width, y + box["height"] * draw_height,
                                         outline="#ffad42" if row["annotation_id"] in self.unsaved_ids else "#55ccee", width=2)

    def _refresh_units(self):
        self.units.delete(0, "end")
        for number, row in enumerate(self._rows(), 1):
            self.units.insert("end", f"{number}: {row['owner']} / {row['source_card']} / {row['form']} / {row['review_status']}")

    def _mark_pending(self):
        frame = self._frame()
        frame["review_status"] = "pending"
        frame["all_identifiable_units_labelled"] = False
        self.frame_review.set("pending")
        self.full_review.set(False)

    def _drag_start(self, event):
        self.drag_origin = (event.x, event.y)

    def _drag_move(self, event):
        if self.drag_origin is None:
            return
        if self.drag_rectangle is not None:
            self.canvas.delete(self.drag_rectangle)
        self.drag_rectangle = self.canvas.create_rectangle(*self.drag_origin, event.x, event.y, outline="#ffad42")

    def _drag_end(self, event):
        if self.drag_origin is None:
            return
        start, self.drag_origin = self.drag_origin, None
        try:
            box = canvas_box_to_normalized((*start, event.x, event.y), self.image_size, self.display_rect)
            frame = self._frame()
            if not self.draft["annotation_sources"]:
                self.draft["annotation_sources"] = [{"annotation_source_id": "pending_units",
                    "path": (self.output_directory / "pending.units.json").relative_to(self.indexes.root).as_posix(), "sha256": "0" * 64}]
            identifier = "unit_" + uuid4().hex
            row = {"annotation_id": identifier,
                   "annotation_source_id": self.draft["annotation_sources"][0]["annotation_source_id"],
                   "recording_id": frame["recording_id"], "frame_id": frame["frame_id"],
                   "deployment_id": None, "owner": "unknown", "source_card": "unknown", "form": "unknown",
                   "visual_class": "minion_unit", "normalized_bbox": dict(zip(("x", "y", "width", "height"), box)),
                   "occlusion": "unknown", "truncation": "unknown", "review_status": "pending"}
            self.draft["unit_annotations"].append(row)
            self.unsaved_ids.add(identifier)
            self._mark_pending()
            frame["minion_presence"] = "positive"
            self.presence.set("positive")
            self._refresh_units()
            self.units.selection_set(len(self._rows()) - 1)
            self._unit_selected()
            self.status.set("新框待复核；填写单位信息，再明确复核整帧。")
        except EvidenceError as exc:
            self.status.set(str(exc))
        self.drag_rectangle = None
        self._render()

    def _unit_selected(self, _event=None):
        selection = self.units.curselection()
        if not selection:
            return
        row = self._rows()[selection[0]]
        for key in ("owner", "source_card", "form", "occlusion", "truncation"):
            getattr(self, key).set(row[key])
        self.deployment.set(row["deployment_id"] or "")
        self.unit_review.set(row["review_status"])

    def _deployment_selected(self, _event=None):
        selected = self.deployment_rows.get(self.deployment.get())
        if selected is not None:
            for key in ("owner", "source_card", "form"):
                getattr(self, key).set(selected[key])

    def _apply_metadata(self):
        selection = self.units.curselection()
        if not selection:
            self.status.set("请先选中一个单位框。")
            return
        row = self._rows()[selection[0]]
        for key in ("owner", "source_card", "form", "occlusion", "truncation"):
            row[key] = getattr(self, key).get()
        row["deployment_id"] = self.deployment.get() or None
        row["review_status"] = self.unit_review.get()
        self._mark_pending()
        self._refresh_units()
        self.units.selection_set(selection[0])
        self.status.set("单位信息已在未保存草稿中更新；整帧仍需复核。")

    def _delete_unsaved(self):
        selection = self.units.curselection()
        if not selection:
            return
        row = self._rows()[selection[0]]
        if row["annotation_id"] not in self.unsaved_ids:
            self.status.set("原有或已保存的框保留；只能删除本次未保存的新框。")
            return
        self.draft["unit_annotations"].remove(row)
        self.unsaved_ids.remove(row["annotation_id"])
        self._mark_pending()
        # Presence is deliberately retained, even after deleting the last box.
        self._refresh_units()
        self._render()

    def _apply_review(self):
        frame = self._frame()
        frame["review_status"] = self.frame_review.get()
        frame["minion_presence"] = self.presence.get()
        frame["all_identifiable_units_labelled"] = self.full_review.get()
        reviewer = self.reviewer.get().strip()
        frame["review_provenance"] = {"method": "manual" if reviewer else "pending", "reviewed_by": reviewer or None,
                                      "notes": self.review_notes.get()}

    def _save(self):
        try:
            self._apply_review()
            validate_dataset_shape(self.draft)
            current = load_dataset_indexes(self.original, self.indexes.root, development_lock_path=self.indexes.development_path)
            if current.development_file_sha256 != self.indexes.development_file_sha256:
                raise EvidenceError("Immutable Development Lock artifact changed before annotation save.")
            identifier = "units_" + uuid4().hex
            output = self.output_directory / (identifier + ".draft.json")
            saved_path = save_annotation_revision({"draft": self.draft, "data_root": self.indexes.root,
                                                   "annotation_source_id": identifier}, output)
            saved = load_evidence(saved_path)
            checked = load_dataset_indexes(saved, self.indexes.root, development_lock_path=self.indexes.development_path)
            self.indexes = checked
            self.original = deepcopy(saved)
            self.draft = deepcopy(saved)
            self.unsaved_ids.clear()
            self.last_saved_path = saved_path
            self._show_frame()
            self.status.set("已追加保存新草稿与标注快照，并重新核对本地绑定。")
        except (EvidenceError, OSError) as exc:
            self.status.set(str(exc) if isinstance(exc, EvidenceError) else "Cannot check local annotation revision.")

    def _next(self):
        try:
            self._apply_review()
            validate_dataset_shape(self.draft)
        except EvidenceError as exc:
            self.status.set(str(exc))
            return
        if self.frame_index + 1 == len(self.draft["frames"]):
            self.status.set("已到最后一帧；未保存的改动仍在草稿中。")
            return
        self.frame_index += 1
        try:
            self._show_frame()
        except (EvidenceError, OSError) as exc:
            self.frame_index -= 1
            self.status.set(str(exc) if isinstance(exc, EvidenceError) else "Cannot open local annotation image.")


def launch_annotator(draft_path: Path, indexes: dict, output_directory: Path) -> None:
    """Recheck explicit local disk context, then open the manual canvas."""
    window = None
    try:
        root = indexes.root
        development_path = indexes.development_path
        path = dataset_artifact_path(root, draft_path.relative_to(root).as_posix())
        folder = dataset_artifact_path(root, output_directory.relative_to(root).as_posix())
        draft = load_evidence(path)
        if not draft["frames"]:
            raise EvidenceError("Annotation requires at least one declared frame.")
        current = load_dataset_indexes(draft, root, development_lock_path=development_path)
        if current.development_file_sha256 != indexes.development_file_sha256:
            raise EvidenceError("Immutable Development Lock artifact changed before annotation launch.")
        import tkinter as tk
        try:
            window = tk.Tk()
        except tk.TclError as exc:
            raise EvidenceError("Cannot initialize local Tk annotation window.") from exc
        _Annotator(window, draft, current, folder)
        window.mainloop()
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("Cannot open checked local unit annotator.") from exc
    finally:
        if window is not None:
            window.destroy()
