import subprocess
import sys

from pydantic import BaseModel, Field

class ExecArgs(BaseModel):
    code: str = Field(description="Python code; the result must be printed with print")


def python_exec(code: str) -> str:
    try:
        r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return "Code exceeded 5 sec"
    out = (r.stdout + r.stderr).strip()
    return out[:5000] if out else "Code ran but the output is empty"
