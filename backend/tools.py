import io
import time
import traceback
import contextlib
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from langchain_core.tools import tool

PLOTS_DIR = Path(__file__).parent.parent / "data" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

SKILLS_DIR = Path(__file__).parent.parent / "skills"

_STATE = {"df": None, "filename": None}

# ---------------------------------------------------------------------
# Execution log: records every code run + resulting plots, regardless of
# which agent/sub-agent triggered it. This is how we recover artifacts
# after the whole (possibly multi-agent) run finishes.
# ---------------------------------------------------------------------
_EXECUTION_LOG = []


def clear_execution_log():
    _EXECUTION_LOG.clear()


def get_execution_log():
    return list(_EXECUTION_LOG)


def load_dataset(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    _STATE["df"] = df
    _STATE["filename"] = Path(filepath).name
    return df


def get_dataset_summary() -> str:
    df = _STATE["df"]
    if df is None:
        return "No dataset loaded."

    buf = io.StringIO()
    df.info(buf=buf)

    return (
        f"Filename: {_STATE['filename']}\n"
        f"Shape: {df.shape}\n"
        f"Columns: {list(df.columns)}\n"
        f"Dtypes:\n{buf.getvalue()}\n"
        f"Sample rows:\n{df.head(3).to_string()}"
    )


@tool
def run_python_code(code: str) -> str:
    """
    Executes Python code against the currently loaded dataset.

    The dataframe is available as `df`. pandas as `pd`, matplotlib.pyplot
    as `plt`, seaborn as `sns` are pre-loaded.

    Assign a text/number answer to a variable named `result` (or print it).
    Any matplotlib/seaborn chart created will be auto-saved as PNG.

    Returns stdout, `result`, saved plot paths, and any error traceback.
    If you see ERROR in the output, fix your code and call this tool again
    (up to 3 attempts).
    """
    df = _STATE["df"]
    if df is None:
        return "ERROR: No dataset has been uploaded yet."

    plt.close("all")

    local_vars = {"df": df, "pd": pd, "plt": plt, "sns": sns}
    stdout_capture = io.StringIO()
    error_trace = None

    try:
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, {"__builtins__": __builtins__}, local_vars)
    except Exception:
        error_trace = traceback.format_exc()

    output_parts = []
    stdout_val = stdout_capture.getvalue().strip()
    if stdout_val:
        output_parts.append(f"STDOUT:\n{stdout_val}")

    if "result" in local_vars:
        output_parts.append(f"RESULT:\n{local_vars['result']}")

    saved_plots = []
    for i, num in enumerate(plt.get_fignums()):
        fig = plt.figure(num)
        filename = f"plot_{int(time.time()*1000)}_{i}.png"
        filepath = PLOTS_DIR / filename
        fig.savefig(filepath, bbox_inches="tight")
        saved_plots.append(str(filepath))
    plt.close("all")

    if saved_plots:
        output_parts.append(f"SAVED_PLOTS:\n{saved_plots}")

    if error_trace:
        output_parts.append(f"ERROR:\n{error_trace}")
        output_parts.append("Please fix the code and try running it again.")

    # Log this execution regardless of success/failure or which agent called it
    _EXECUTION_LOG.append({
        "code": code,
        "success": error_trace is None,
        "plots": saved_plots,
    })

    if not output_parts:
        output_parts.append(
            "Code executed with no output. "
            "Remember to print() something or assign to `result`."
        )

    return "\n\n".join(output_parts)


@tool
def list_skills() -> str:
    """Lists available skill guides with short descriptions.
    Call this before read_skill to see what guides exist."""
    lines = []
    for folder in sorted(SKILLS_DIR.iterdir()):
        skill_file = folder / "SKILL.md"
        if skill_file.exists():
            meta = _parse_frontmatter(skill_file.read_text())
            lines.append(f"- {folder.name}: {meta.get('description', '')}")
    return "\n".join(lines) if lines else "No skills found."


@tool
def read_skill(skill_name: str) -> str:
    """Reads the full instructions of a skill by folder name
    (e.g. 'eda', 'cleaning', 'plotting', 'insights')."""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return f"No skill named '{skill_name}'. Use list_skills to see options."
    return skill_file.read_text()


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta