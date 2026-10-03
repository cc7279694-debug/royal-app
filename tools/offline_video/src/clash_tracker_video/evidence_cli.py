"""Three-command local evidence CLI, independent of Module 1 CLI."""
import argparse
import sys
from pathlib import Path

from .evidence_contract import EvidenceError, load_evidence, validate_evidence
from .evidence_prepare import prepare_evidence, load_indexes, safe_path


class Parser(argparse.ArgumentParser):
    def error(self,message):
        raise EvidenceError('Invalid command arguments; use --help.')


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description='Local manual evidence; no card recognition.')
    sub = parser.add_subparsers(dest='command',required=True,parser_class=Parser)
    prepare = sub.add_parser('prepare')
    prepare.add_argument('input')
    prepare.add_argument('--recording-id',required=True)
    prepare.add_argument('--output',required=True)
    prepare.add_argument('--times',nargs='+',type=float)
    validate = sub.add_parser('validate')
    validate.add_argument('evidence')
    validate.add_argument('--indexes',nargs='+',required=True)
    try:
        args = parser.parse_args(argv)
        if args.command == 'prepare':
            index = prepare_evidence(args.input,args.output,recording_id=args.recording_id,times=args.times)
            print(f"Preparation: {index['status']}")
            return 0 if index['status']=='success' else 3
        doc = load_evidence(safe_path(args.evidence,private=True))
        indexes = load_indexes(args.indexes)
        errors = validate_evidence(doc,indexes)
        if errors:
            print(f'Invalid evidence: {len(errors)} validation errors.',file=sys.stderr)
            return 2
        print('Evidence valid.')
        return 0
    except (EvidenceError,OSError,ValueError) as exc:
        print(str(exc) if isinstance(exc,EvidenceError) else 'Local evidence I/O failed.',file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
