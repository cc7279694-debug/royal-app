"""Three-command local evidence CLI, independent of Module 1 CLI."""
import argparse
import sys
from pathlib import Path

from .evidence_contract import EvidenceError, load_evidence, validate_evidence
from .evidence_prepare import prepare_evidence, load_indexes, safe_path, new_output, write_json
from .evidence_review import review_evidence


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
    review = sub.add_parser('review')
    review.add_argument('evidence')
    review.add_argument('--indexes',nargs='+',required=True)
    review.add_argument('--output',required=True)
    try:
        args = parser.parse_args(argv)
        if args.command == 'prepare':
            index = prepare_evidence(args.input,args.output,recording_id=args.recording_id,times=args.times)
            print(f"Preparation: {index['status']}")
            return 0 if index['status']=='success' else 3
        doc = load_evidence(safe_path(args.evidence,private=True))
        indexes = load_indexes(args.indexes)
        if args.command == 'review':
            report = review_evidence(doc,indexes)
            destination = new_output(args.output,directory=False)
            write_json(destination,dict(schema_version=1,**report))
            print(f"Review: {report['status']}; candidate_gate={report['candidate_gate']}; experiment_gate=False")
            return 2 if report['status']=='invalid' else 3
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
