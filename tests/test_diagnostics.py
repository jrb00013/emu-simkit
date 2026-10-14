from emu_simkit.diagnostics.log_parse import parse_log
from emu_simkit.diagnostics.report import DiagnosticReport, report_to_json


def test_parse_log(tmp_path):
    log = tmp_path / "emu.log"
    log.write_text(
        "info starting\n"
        "WARNING hang suspected\n"
        "Fatal Access violation writing location 0x17\n"
        "PPU[0x1] CIA: 0x1234\n",
        encoding="utf-8",
    )
    s = parse_log(log)
    assert s.lines == 4
    assert s.fatals
    assert s.warnings
    report = DiagnosticReport.from_log(log)
    text = report_to_json(report)
    assert "fatal_count" in text
