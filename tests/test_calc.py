import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from components.virtual_calc import eval_safe

def test_calc_eval():
    print("Testing Calculator Safe Eval...")
    assert eval_safe("2 + 3 * 4") == 14
    assert eval_safe("2 ^ 3") == 8
    assert round(eval_safe("math.sin(math.pi / 2)"), 5) == 1.0
    assert eval_safe("10 / 4") == 2.5
    print("  -> Passed!")

if __name__ == "__main__":
    test_calc_eval()
