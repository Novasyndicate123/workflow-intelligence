import argparse

from core.manual_response_intake import ManualResponseIntake
from core.smb_response_evidence import SMBResponseEvidenceStore


class OperatorResponseConsole:
    def __init__(self, results_path="results/smb_response_evidence.jsonl"):
        self.intake = ManualResponseIntake(SMBResponseEvidenceStore(results_path))

    def record(self, experiment_run_id, classification, note, consent, source_channel):
        row = self.intake.record(
            experiment_run_id=experiment_run_id,
            classification=classification,
            note=note,
            consent=consent,
            source_channel=source_channel,
        )
        row.update({
            "status": "RECORDED",
            "promoted": False,
            "execution_authorized": False,
            "external_send_authorized": False,
            "revenue_verified": False,
            "economic_outcome_verified": False,
        })
        return row


def build_parser():
    parser = argparse.ArgumentParser(description="Workflow Intelligence manual response console")
    parser.add_argument("--experiment-run-id", required=True)
    parser.add_argument("--classification", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--consent", choices=("yes", "no"), required=True)
    parser.add_argument("--source-channel", required=True)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    row = OperatorResponseConsole().record(
        experiment_run_id=args.experiment_run_id,
        classification=args.classification,
        note=args.note,
        consent=args.consent == 'yes',
        source_channel=args.source_channel,
    )
    for key in ('status', 'response_id', 'promoted', 'execution_authorized', 'external_send_authorized'):
        print(f'{key}={row[key]}')


if __name__ == '__main__':
    main()
