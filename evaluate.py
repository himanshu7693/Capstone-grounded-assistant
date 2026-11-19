"""
Evaluate the guardrailed assistant against evaluation_set.json.

The evaluator checks whether:
- in-scope questions are allowed,
- off-topic questions are refused,
- unsafe questions are refused.

It also reports measured token usage and estimated cost for allowed calls.
"""

import json
from pathlib import Path

from app import ask_assistant


def main():
    path = Path(__file__).parent / "evaluation_set.json"
    cases = json.loads(path.read_text(encoding="utf-8"))

    passed = 0
    total_input = 0
    total_output = 0
    total_cost = 0.0
    rows = []

    for case in cases:
        result = ask_assistant(case["input"])
        expected = case["expected_decision"]
        ok = result.decision == expected

        passed += int(ok)
        total_input += result.input_tokens
        total_output += result.output_tokens
        total_cost += result.estimated_cost_usd

        rows.append((case["id"], ok, expected, result.decision))

    score = passed / len(cases) * 100

    print("\nEvaluation results")
    print("=" * 60)
    for case_id, ok, expected, actual in rows:
        status = "PASS" if ok else "FAIL"
        print(
            f"{status:4} {case_id:>3} | expected={expected:<10} | actual={actual}"
        )

    print("=" * 60)
    print(f"Passed: {passed}/{len(cases)}")
    print(f"Score: {score:.1f}%")
    print(f"Input tokens measured: {total_input}")
    print(f"Output tokens measured: {total_output}")
    print(f"Estimated API cost: ${total_cost:.6f}")


if __name__ == "__main__":
    main()
