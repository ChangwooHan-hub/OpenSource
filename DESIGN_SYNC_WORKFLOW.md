# AST-SDR-SAR Design Synchronization

## Goal

This MVP implements the workflow:

```text
C/C++ git commit
  -> changed file detection
  -> AST Parser
  -> SDR_Agent updates design/UnitDesign.xmi
  -> SAR_Agent reviews design/Architecture.xmi vs design/UnitDesign.xmi
  -> Enterprise Architect imports XMI
```

The original workflow referenced Claude models. This implementation uses GPT through the OpenAI Responses API when `OPENAI_API_KEY` is configured. XMI generation remains deterministic so malformed model output cannot corrupt the UML files.

## Agent Roles

| Agent | Responsibility | Default GPT model |
| --- | --- | --- |
| `SDR_Agent` | Convert changed C/C++ AST facts into unit design XMI and write an SDR report. | `gpt-5.2` |
| `SAR_Agent` | Compare unit design against architecture XMI and write architecture review findings. | `gpt-5.2` |

Models and paths are configured in `agents/config.yaml`.

## Implemented Phases

1. AST Parser
   - `agents/ast_parser.py`
   - Uses Python `clang` bindings when installed.
   - Falls back to a deterministic parser for C/C++ classes, C `typedef struct`, C `typedef enum`, functions, includes, members, and parameters.

2. XMI Manager
   - `agents/xmi_manager.py`
   - Creates UML 2.x style XMI with:
     - `xmlns:xmi="http://www.omg.org/XMI"`
     - `xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML"`
   - Updates generated unit design elements without deleting unrelated manual XMI elements.

3. SDR MVP
   - `agents/sdr_agent.py`
   - Inputs changed files, parses AST, updates `design/UnitDesign.xmi`, and writes `design/reports/SDRReport_*.md`.
   - GPT notes are optional and skipped when `OPENAI_API_KEY` is absent.

4. SAR MVP
   - `agents/sar_agent.py`
   - Reads `design/Architecture.xmi` and `design/UnitDesign.xmi`.
   - Reports classes/structs/enums that lack an architecture component owner and dependency targets missing from both models.
   - Writes `design/reports/ReviewReport_*.md`.

5. Git Hook Integration
   - `scripts/post-commit`
   - `scripts/install_git_hook.ps1`
   - Installed target: `.git/hooks/post-commit`
   - Disable for one commit/session with `DISABLE_DESIGN_HOOK=1`.

## Usage

From `process`, install dependencies:

```powershell
pip install -r requirements.txt
```

From `process`, run the pipeline for explicit files:

```powershell
python agents\pipeline.py Seat\src\voltage_fail.c Seat\inc\voltage_fail.h
```

Run for files changed in the last commit:

```powershell
python agents\pipeline.py --changed-in-last-commit
```

Install the git hook:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_git_hook.ps1
```

## Enterprise Architect Import

Import these files in EA:

1. `design/Architecture.xmi`
2. `design/UnitDesign.xmi`

Use `File > Import > Import Package from XMI`, then save the EA project as `.qea`.
