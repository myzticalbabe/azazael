# coding: utf-8
"""Unit tests for evolution helpers + Terence verify/rollback.

Covers B6 gaps on evolution_cycle.py (deterministic helpers only — the
full lifecycle stays proven via live logs) and locks in the Terence
proficiency ladder (good/bad/stale fixes).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import evolution_cycle as evc


class TestGenomeSeed:
    def test_deterministic(self):
        g = {"learning_rate": 0.3, "epsilon": 0.1, "discount": 0.9,
             "epsilon_decay": 0.05}
        assert evc.genome_seed(g, "a") == evc.genome_seed(g, "a")

    def test_salts_differ(self):
        g = {"learning_rate": 0.3, "epsilon": 0.1, "discount": 0.9,
             "epsilon_decay": 0.05}
        seeds = {evc.genome_seed(g, s) for s in evc._SALTS}
        assert len(seeds) == len(evc._SALTS) == 3

    def test_genomes_differ(self):
        g1 = {"learning_rate": 0.3, "epsilon": 0.1, "discount": 0.9,
              "epsilon_decay": 0.05}
        g2 = dict(g1, learning_rate=0.31)
        assert evc.genome_seed(g1) != evc.genome_seed(g2)

    def test_key_order_stable(self):
        g1 = {"epsilon": 0.1, "learning_rate": 0.3, "discount": 0.9,
              "epsilon_decay": 0.05}
        g2 = {"learning_rate": 0.3, "discount": 0.9, "epsilon": 0.1,
              "epsilon_decay": 0.05}
        assert evc.genome_seed(g1) == evc.genome_seed(g2)


class TestTerenceVerify:
    def _fix(self, path, line, original, fixed):
        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), '..', 'src',
                            'UTILITIES', 'TERENCE'))
        from TERENCE import TERENCE, Fix
        return TERENCE(), Fix(str(path), line, "bare-except", original, fixed,
                            "test fix")

    def test_good_fix_applies(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("try:\n    x = 1\nexcept:\n    pass\n")
        t, fix = self._fix(p, 3, "except:", "except Exception:")
        ok, reason = t._apply_verified(fix)
        assert ok, reason
        assert "except Exception:" in p.read_text()

    def test_breaking_fix_rolls_back(self, tmp_path):
        p = tmp_path / "a.py"
        before = "x = 1\n"
        p.write_text(before)
        t, fix = self._fix(p, 1, "x = 1", "x = (1")
        ok, reason = t._apply_verified(fix)
        assert not ok
        assert p.read_text() == before

    def test_stale_line_rejected(self, tmp_path):
        p = tmp_path / "a.py"
        p.write_text("y = 2\n")
        t, fix = self._fix(p, 1, "x = 1", "x = 2")
        ok, reason = t._apply_verified(fix)
        assert not ok and "drifted" in reason
        assert p.read_text() == "y = 2\n"

    def test_non_utf8_skipped_intact(self, tmp_path):
        p = tmp_path / "a.py"
        raw = b"x = '\xff\xfe not utf8'\n"
        p.write_bytes(raw)
        t, fix = self._fix(p, 1, "x =", "x ==")
        ok, reason = t._apply_verified(fix)
        assert not ok and "UTF8" in reason
        assert p.read_bytes() == raw

    def test_locked_file_rejected(self, tmp_path):
        import msvcrt
        p = tmp_path / "a.py"
        p.write_text("x = 1\n")
        lfh = open(str(p) + ".terence.lock", "w")
        msvcrt.locking(lfh.fileno(), msvcrt.LK_NBLCK, 1)
        try:
            t, fix = self._fix(p, 1, "x = 1", "x = 2")
            ok, reason = t._apply_verified(fix)
            assert not ok and "locked" in reason
            assert p.read_text() == "x = 1\n"
        finally:
            lfh.close()
            try:
                import os as _os
                _os.remove(str(p) + ".terence.lock")
            except OSError:
                pass
