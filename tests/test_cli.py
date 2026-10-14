from emu_simkit.cli import build_parser


def test_parser_smoke():
    p = build_parser()
    args = p.parse_args(["backends"])
    assert args.command == "backends"
