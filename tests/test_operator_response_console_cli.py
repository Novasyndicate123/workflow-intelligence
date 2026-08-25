from core.operator_response_console import build_parser


def test_parser_accepts_required_fields():
    parser = build_parser()
    args = parser.parse_args([
        '--experiment-run-id', '78fa7486907c4da8b851a8e01a729f58',
        '--classification', 'problem_confirmed',
        '--note', 'Manual test note',
        '--consent', 'yes',
        '--source-channel', 'manual_review',
    ])
    assert args.experiment_run_id == '78fa7486907c4da8b851a8e01a729f58'
    assert args.consent == 'yes'


def test_parser_requires_note():
    parser = build_parser()
    try:
        parser.parse_args([
            '--experiment-run-id', 'run-1',
            '--classification', 'problem_confirmed',
            '--consent', 'yes',
            '--source-channel', 'manual_review',
        ])
    except SystemExit:
        return
    raise AssertionError('note must be required')


def test_main_emits_recorded_result(monkeypatch, capsys):
    from core import operator_response_console as module

    class FakeConsole:
        def record(self, **kwargs):
            return {
                'status': 'RECORDED',
                'response_id': 'resp-1',
                'promoted': False,
                'execution_authorized': False,
                'external_send_authorized': False,
            }

    monkeypatch.setattr(module, 'OperatorResponseConsole', FakeConsole)
    module.main([
        '--experiment-run-id', 'run-1',
        '--classification', 'problem_confirmed',
        '--note', 'Observed workflow pain',
        '--consent', 'yes',
        '--source-channel', 'manual_review',
    ])
    out = capsys.readouterr().out
    assert 'RECORDED' in out
    assert 'external_send_authorized=False' in out
