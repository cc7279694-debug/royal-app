"""Separate local Phase A commands, not training or Model Lock permission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .evidence_contract import EvidenceError, load_evidence
from .multiclass_dataset import (bind_multiclass, freeze_scale_snapshot, load_scale_snapshot,
                                freeze_multiclass_dataset, load_multiclass_dataset_lock)
from .multiclass_export import export_multiclass_dataset
from .multiclass_readiness import development_scale_report, multiclass_readiness
from .training_dataset import _disk_operation, dataset_artifact_path, private_artifact_path


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["allow_abbrev"] = False
        super().__init__(*args, **kwargs)

    def error(self, message):
        raise EvidenceError("Invalid multiclass arguments; use --help.")


def _artifact(value, root):
    path = private_artifact_path(Path(value).absolute())
    return dataset_artifact_path(root, path.relative_to(root).as_posix())


@_disk_operation
def main(argv: list[str] | None = None) -> int:
    parser = Parser(description="Checked offline multiclass data preparation; no training authorization.")
    subs = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    for name in ("validate-dataset", "scale-report", "freeze-scale", "freeze-dataset",
                 "validate-dataset-lock", "annotate", "export"):
        command = subs.add_parser(name)
        command.add_argument("input")
        command.add_argument("--data-root", required=True)
        if name in ("validate-dataset", "scale-report", "freeze-dataset"):
            command.add_argument("--scale-snapshot", required=name == "freeze-dataset")
        if name in ("freeze-scale", "freeze-dataset", "annotate", "export"):
            command.add_argument("--output", required=True)
        if name == "export":
            command.add_argument("--backend", required=True, choices=("yolox", "torchvision"))
    try:
        args = parser.parse_args(argv)
        root = Path(args.data_root)
        path = _artifact(args.input, root)
        if args.command == "validate-dataset-lock":
            load_multiclass_dataset_lock(path, root)
            print("Multiclass dataset lock valid.")
            return 0
        if args.command == "export":
            manifest = export_multiclass_dataset(path, data_root=root, backend=args.backend,
                                                output_directory=_artifact(args.output, root))
            print(json.dumps({"backend": manifest["backend"], "counts": manifest["counts"]}, allow_nan=False))
            return 0
        bound = bind_multiclass(load_evidence(path), root)
        snapshot = (load_scale_snapshot(_artifact(args.scale_snapshot, root), root)
                    if getattr(args, "scale_snapshot", None) else None)
        if args.command in ("validate-dataset", "scale-report"):
            report = multiclass_readiness(bound.draft, dict(snapshot) if snapshot is not None else None)
            if report["status"] == "INVALID_DATASET":
                raise EvidenceError("Invalid or stale multiclass readiness input.")
            result = development_scale_report(bound.draft) if args.command == "scale-report" else report
            print(json.dumps(result, allow_nan=False, sort_keys=True))
            return 0 if report["ready"] else 3
        output = _artifact(args.output, root)
        if args.command == "freeze-scale":
            freeze_scale_snapshot(bound, output)
            print("Multiclass preselection scale snapshot frozen.")
            return 0
        if args.command == "freeze-dataset":
            freeze_multiclass_dataset(bound, snapshot, output)
            print("MULTICLASS_DATASET_LOCKED")
            return 0
        # Only explicit annotation launch imports Tk; read-only/help has none.
        from tkinter import TclError
        from .multiclass_annotation import launch_multiclass_annotator
        try:
            launch_multiclass_annotator(path, data_root=root, output_directory=output)
        except TclError as exc:
            raise EvidenceError("Cannot use local multiclass annotation window.") from exc
        print("Multiclass annotation session closed.")
        return 0
    except SystemExit as exc:
        return int(exc.code or 0)
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, AttributeError,
            OverflowError, RecursionError, RuntimeError, ImportError):
        print("Invalid multiclass command or local evidence.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
