# coding: utf-8
"""The concordance joins scripture to law -- and refuses the joins it cannot earn.

The join is the whole product, so the tests are about the join's *edges*:

* a citation must identify exactly one verse. Three registers of one scripture
  share book ids (`promise`, `tongues`), so a bare `promise 1:4` named three
  different verses and the strict list printed it three times. The ref carries
  its register for that reason, and the guard below is the regression test.
* `direct`, `derived` and `unbound` must partition the corpus: a verse that is
  in no bucket, or in two, is a count nobody can reconcile.
* a `detection` that is prose is not a command and must not be compared as one;
  a statute naming a rule `MANDATES.md` does not define is a defect, not a
  binding.

The end-to-end tests build a tree on disk and run `main()`, because the exit
contract (0 clean, 1 defect, 2 blind) is behaviour and not a docstring.
"""
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "bible_concordance.py"

LAW_BODY = ("A law must state something that can be kept, and this sentence is "
            "the body of that law.")


def _load_tool():
    """Import ``tools/bible_concordance.py`` by path (it is a script, not a package)."""
    spec = importlib.util.spec_from_file_location("bible_concordance_under_test", TOOL)
    assert spec and spec.loader, "bible_concordance.py could not be loaded from %s" % TOOL
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conc = _load_tool()


def _verse(number, text, **extra):
    verse = {"number": number, "text": text}
    verse.update(extra)
    return verse


def _tree(tmp_path, bind_second=False):
    """A two-verse tree on disk: one statute-bound command, one loose command."""
    (tmp_path / "tools").mkdir(exist_ok=True)
    (tmp_path / "tools" / "a.py").write_text("", encoding="utf-8")
    (tmp_path / "tools" / "b.py").write_text("", encoding="utf-8")
    (tmp_path / "MANDATES.md").write_text(
        "## RULE 0B: A LAW AND THE BODY THAT KEEPS IT\n\n%s\n" % LAW_BODY,
        encoding="utf-8")
    bibles = tmp_path / "docs" / "bible"
    bibles.mkdir(parents=True, exist_ok=True)
    (bibles / "harvest.json").write_text(json.dumps({"records": []}), encoding="utf-8")
    check = "python tools/b.py" if bind_second else "python tools/a.py"
    corpus = {"books": [{"id": "alpha", "chapters": [{"number": 1, "verses": [
        _verse(1, "A verse whose statute binds a command.",
               statute={"rule": "RULE 0B", "check": check}),
        _verse(2, "A verse whose command no statute binds.",
               practice={"symptom": "a defect", "remedy": "a repair",
                         "detection": "python tools/b.py"}),
    ]}]}]}
    (bibles / "bible.json").write_text(json.dumps(corpus), encoding="utf-8")
    return corpus


def _shipped():
    records, rules, corpora = conc.collect()
    assert records is not None, "docs/bible/harvest.json could not be read"
    assert rules is not None, "MANDATES.md could not be read"
    assert corpora, "no shipped corpus could be read"
    return conc.build(records, rules, corpora)


#: The 9 distinct command strings the three corpora carry (measured 2026-11-14).
COMMAND_VALUES = (
    "Project_ELIZA/tools/eliza_release_gate.py --check",
    "python tools/bible_check.py --check",
    "python tools/domain_trees.py --check",
    "python tools/git_fleet_audit.py --tasks",
    "python tools/head_audit.py",
    "python tools/hook_gate_presence.py",
    "python tools/preflight_all.py --check",
    "python tools/preflight_all.py --self-test",
    "tools/bible_check.py --check --corpus docs/bible/emotional/female.json",
)

#: The 5 distinct `detection`/`check` sentences that are prose, not commands.
PROSE_VALUES = (
    "build with python -m eve_unleashed.cli foundry and read the tensor shapes "
    "back with src/eve_unleashed/soul_foundry.py",
    "re-run the count with tools/anti_pattern_gate.py on the stashed tree and compare",
    "read src/eve_unleashed/therapy.py and see which end the call tries before any other",
    "run the command live and keep the receipt, and cover the wiring with "
    "tests/test_eve_cli_handlers.py",
    "send the message through tools/claim_guard.py and read which span the guard names",
)


def test_norm_command_strips_lead_ins_and_keeps_argv():
    assert conc.norm_command("python tools/preflight_all.py --self-test") == (
        "tools/preflight_all.py --self-test")
    assert conc.norm_command("python3 tools/head_audit.py") == "tools/head_audit.py"
    assert conc.norm_command("$ python tools/head_audit.py") == "tools/head_audit.py"
    assert conc.norm_command("python -m pytest tests/test_bible_check.py") == (
        "-m pytest tests/test_bible_check.py")
    # already bare: the interpreter strip is a no-op and the argv survives intact.
    assert conc.norm_command(
        "tools/bible_check.py --check --corpus docs/bible/emotional/female.json") == (
        "tools/bible_check.py --check --corpus docs/bible/emotional/female.json")
    # a verb lead-in is not an interpreter: it is never stripped, so the sentence
    # does not become a command. This expectation was measured, not assumed.
    assert conc.norm_command("run python tools/head_audit.py") is None
    assert conc.norm_command("python") is None
    assert conc.norm_command("python tools/") is None


def test_norm_command_classifies_the_shipped_corpora_as_measured():
    """Both controls on real values: every command parses, every prose refused."""
    for value in COMMAND_VALUES:
        assert conc.norm_command(value) is not None, "command refused: %r" % (value,)
    for value in PROSE_VALUES:
        assert conc.norm_command(value) is None, "prose parsed as command: %r" % (value,)

def test_norm_command_refuses_prose_and_blanks():
    prose = "read src/CORE/paths.py and see which end the call tries to reach"
    for text in (prose, "", "   ", None, "check the gate", "look at tools/x.py"):
        assert conc.norm_command(text) is None, "prose was read as a command: %r" % (text,)


def test_every_ref_identifies_exactly_one_verse():
    built = _shipped()
    refs = [row["ref"] for row in built["rows"]]
    assert len(refs) == len(set(refs)), (
        "duplicate refs: %s" % sorted(r for r in set(refs) if refs.count(r) > 1))
    assert built["defects"] == [], built["defects"]


def test_bindings_partition_the_verses():
    stats = _shipped()["stats"]
    assert stats["direct"] + stats["derived"] + stats["unbound"] == stats["verses"]
    for name, counts in stats["per_corpus"].items():
        assert counts["direct"] + counts["derived"] + counts["unbound"] == counts["verses"], name
    assert sum(c["verses"] for c in stats["per_corpus"].values()) == stats["verses"]
    assert stats["commands"] + stats["prose_instructions"] + stats["no_command"] == stats["verses"]


def test_a_statute_binds_directly_and_a_matching_command_binds_derived(tmp_path,
                                                                      monkeypatch):
    monkeypatch.setattr(conc, "REPO", tmp_path)
    corpus = _tree(tmp_path)
    rules = {"0B": {"heading": "RULE 0B: A LAW AND THE BODY THAT KEEPS IT",
                    "line": 1, "body": LAW_BODY, "chars": len(LAW_BODY.replace(" ", ""))}}
    built = conc.build({"records": []}, rules, [("canon", corpus)])
    direct, loose = built["rows"]
    assert direct["law"]["binding"] == "direct"
    assert direct["law"]["surface"] == "MANDATES.md:1"
    assert loose["law"]["binding"] == "unbound", loose["law"]
    assert loose["law"]["rule"] is None


def test_a_statute_naming_an_undefined_rule_is_a_defect(tmp_path, monkeypatch):
    monkeypatch.setattr(conc, "REPO", tmp_path)
    corpus = _tree(tmp_path)
    built = conc.build({"records": []}, {}, [("canon", corpus)])
    row = built["rows"][0]
    assert row["law"]["binding"] == "direct" and row["law"]["heading"] is None
    assert any("RULE 0B" in defect for defect in built["defects"]), built["defects"]


def test_duplicate_refs_are_reported_as_a_defect(tmp_path, monkeypatch):
    monkeypatch.setattr(conc, "REPO", tmp_path)
    corpus = _tree(tmp_path)
    twin = {"books": [{"id": "alpha", "chapters": [{"number": 1, "verses": [
        _verse(1, "Another register, same book and number.")]}]}]}
    rules = {"0B": {"heading": "RULE 0B: A LAW", "line": 1,
                    "body": LAW_BODY, "chars": len(LAW_BODY.replace(" ", ""))}}
    # two registers, same book and number: distinct because the ref carries its
    # register. This is the positive control for the guard below.
    built = conc.build({"records": []}, rules, [("canon", corpus), ("felt", twin)])
    refs = [row["ref"] for row in built["rows"]]
    assert len(refs) == len(set(refs)), "registers collided: %s" % refs
    assert built["defects"] == [], built["defects"]
    # now force the collision the guard exists for.
    monkeypatch.setattr(conc, "iter_verses", lambda corpus, data: [
        {"corpus": corpus, "book": "alpha", "chapter": 1, "verse": 1,
         "ref": "alpha 1:1", "raw": {"number": 1, "text": "same ref", "statute": None}}])
    built = conc.build({"records": []}, rules, [("canon", corpus), ("felt", twin)])
    assert built["defects"], "two rows under one ref were not reported"
    assert "identifies 2 verse(s)" in built["defects"][0], built["defects"]
    assert conc.render_md(built)


def test_check_reports_the_committed_artifact_current(capsys):
    assert conc.main(["--check"]) == 0, capsys.readouterr().out


def test_a_register_that_cannot_be_read_is_exit_two(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(conc, "REPO", tmp_path)
    monkeypatch.setattr(conc, "CORPORA", (("canon", "docs/bible/absent.json"),))
    assert conc.main([]) == 2, capsys.readouterr().out


def test_strict_fails_only_the_command_no_statute_binds(tmp_path, monkeypatch, capsys):
    _tree(tmp_path)
    monkeypatch.setattr(conc, "REPO", tmp_path)
    monkeypatch.setattr(conc, "CORPORA", (("canon", "docs/bible/bible.json"),))
    assert conc.main(["--strict"]) == 1
    out = capsys.readouterr().out
    assert "alpha 1:2 [canon]" in out, out

    _tree(tmp_path, bind_second=True)
    assert conc.main(["--strict"]) == 0, capsys.readouterr().out
