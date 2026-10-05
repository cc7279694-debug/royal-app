"""Checked, private data preparation commands; no training or model permission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .evidence_contract import EvidenceError, load_evidence
from .experiment_lock import load_lock
from .training_dataset import (bind_dataset, dataset_artifact_path, freeze_dataset,
                               load_dataset_indexes, load_dataset_lock,
                               private_artifact_path, validate_dataset_lock)


class Parser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["allow_abbrev"] = False
        super().__init__(*args, **kwargs)

    def error(self, message):
        raise EvidenceError("Invalid training dataset arguments; use --help.")


def _artifact(value, root: Path) -> Path:
    path = private_artifact_path(Path(value).absolute())
    return dataset_artifact_path(root, path.relative_to(root).as_posix())


def _summary(report: dict) -> dict:
    # Per-recording/match identities and external bindings remain private.
    return {key: report[key] for key in ("valid", "training_data_ready", "evaluation_ready",
            "counts", "reasons", "evaluation_reasons", "confirmed_absent_seconds", "coverage_scope")}


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description="Private local dataset preparation; readiness does not authorize training.")
    subs = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    for name in ("validate-dataset", "freeze-dataset", "validate-dataset-lock", "annotate"):
        command = subs.add_parser(name)
        command.add_argument("input")
        command.add_argument("--data-root", required=True)
        command.add_argument("--development", required=True)
        if name in {"freeze-dataset", "annotate"}:
            command.add_argument("--output", required=True)
    try:
        args = parser.parse_args(argv)
        root = Path(args.data_root)
        path = _artifact(args.input, root)
        development_path = _artifact(args.development, root)
        document = load_evidence(path)
        development = load_lock(development_path)
        if args.command == "validate-dataset-lock":
            validate_dataset_lock(document, development)
            draft = document["payload"]["draft"]
        else:
            draft = document
        indexes = load_dataset_indexes(draft, root, development_lock_path=development_path)

        if args.command == "validate-dataset-lock":
            load_dataset_lock(path, development, indexes)
            print("Training dataset lock valid.")
            return 0

        payload = bind_dataset(draft, indexes, development)
        if args.command == "validate-dataset":
            report = payload["derived"]
            print(json.dumps(_summary(report), allow_nan=False))
            return 0 if report["training_data_ready"] else 3

        output = _artifact(args.output, root)
        if args.command == "annotate":
            # Importing the CLI or validating data never creates a Tk window.
            from tkinter import TclError
            from .unit_annotation import launch_annotator
            try:
                launch_annotator(path, indexes, output)
            except TclError as exc:
                raise EvidenceError("Cannot use local annotation window.") from exc
            print("Annotation session closed.")
            return 0

        lock = freeze_dataset(payload, output)
        lock_path = output / f"{lock['dataset_id']}.training_dataset.v{lock['freeze_version']}.json"
        fresh_indexes = load_dataset_indexes(draft, root, development_lock_path=development_path)
        load_dataset_lock(lock_path, development, fresh_indexes)
        print("Training dataset locked.")
        return 0
    except SystemExit as exc:
        # argparse help is a normal, non-mutating command, including main(argv).
        return int(exc.code or 0)
    except (EvidenceError, OSError, ValueError, TypeError, KeyError, AttributeError,
            OverflowError, RecursionError, RuntimeError, ImportError):
        print("Invalid training dataset command or local evidence.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
