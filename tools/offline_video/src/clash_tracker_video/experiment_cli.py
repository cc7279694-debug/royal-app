"""Local experiment readiness and immutable locks; no models or inference."""
import argparse
import sys

from .evidence_contract import EvidenceError, load_evidence
from .evidence_prepare import load_indexes, safe_path
from .experiment_development import _index_snapshot, validate_development
from .experiment_lock import canonical_bytes, freeze_development, freeze_test_gt, load_lock


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise EvidenceError("Invalid command arguments; use --help.")


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description="Local experiment evidence and lock contracts; no inference.")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    readiness = sub.add_parser("readiness")
    readiness.add_argument("draft")
    readiness.add_argument("--indexes", nargs="+", required=True)
    development = sub.add_parser("freeze-development")
    development.add_argument("draft")
    development.add_argument("--indexes", nargs="+", required=True)
    development.add_argument("--output", required=True)
    validate = sub.add_parser("validate-lock")
    validate.add_argument("lock")
    validate.add_argument("--development")
    validate.add_argument("--model")
    test = sub.add_parser("freeze-test-gt")
    test.add_argument("ground_truth")
    test.add_argument("--development", required=True)
    test.add_argument("--model", required=True)
    test.add_argument("--indexes", nargs="+", required=True)
    test.add_argument("--output", required=True)
    try:
        args = parser.parse_args(argv)
        if args.command in {"readiness", "freeze-development"}:
            draft = load_evidence(safe_path(args.draft, private=True))
            indexes = load_indexes(args.indexes)
            if args.command == "readiness":
                report = validate_development(draft, indexes)
                if not report["valid"]:
                    raise EvidenceError("Invalid development evidence.")
                print(f"Readiness: {report['status']}.")
                return 0 if report["status"] == "DEV_VALIDATED" else 3
            freeze_development(draft, indexes, args.output)
            print("Development: DEV_LOCKED.")
            return 0

        development_lock = load_lock(args.development) if args.development else None
        model_lock = load_lock(args.model, development_lock) if args.model else None
        if args.command == "validate-lock":
            load_lock(args.lock, development_lock, model_lock)
            print("Lock valid.")
            return 0

        gt = load_evidence(safe_path(args.ground_truth, private=True))
        indexes = load_indexes(args.indexes)
        pseudo = {"identity": {"recording_id": gt["identity"]["recording_id"]},
                  "candidates": [{"evidence": {"frame_annotations": [
                      frame for play in gt["deployments"] for frame in play["key_frames"]]}}]}
        actual = _index_snapshot(pseudo, indexes)
        if canonical_bytes(actual) != canonical_bytes(gt["index_snapshot"]):
            raise EvidenceError("Ground-truth snapshot differs from actual disk evidence.")
        freeze_test_gt(gt, development_lock, model_lock, args.output)
        print("Test GT locked.")
        return 0
    except (EvidenceError, OSError, ValueError, TypeError, KeyError,
            AttributeError, OverflowError, RecursionError):
        # Never echo argparse input, private paths, arbitrary schema values, or
        # lower-level exception text. Detailed evidence remains in private files.
        print("Invalid experiment command or local evidence.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
