"""Verify the TEST_FAILURE_MANDATE and CONCURRENT_INFERENCE_MANDATE are codified and loadable."""
import os
import sys


def test_mandate_exists():
    """Verify that both TEST_FAILURE_MANDATE and CONCURRENT_INFERENCE_MANDATE are codified and loadable."""
    file_path = os.path.join(
        os.path.dirname(__file__), "..", "..", ".codebuff", "rules.md"
    )
    assert os.path.exists(file_path), f"Mandate file must exist at {file_path}"

    with open(file_path, "r") as f:
        content = f.read()

    assert "TEST_FAILURE_MANDATE" in content, "Mandate must be explicitly defined"
    assert "thinker-with-files-gemini" in content, "Mandate must enforce Gemini usage"
    assert "CONCURRENT_INFERENCE_MANDATE" in content, "CONCURRENT_INFERENCE_MANDATE must be defined"
    assert "spawn_agents" in content, "CONCURRENT_INFERENCE_MANDATE must enforce concurrent spawning"


if __name__ == "__main__":
    test_mandate_exists()
    print("Both mandates verified successfully.")
