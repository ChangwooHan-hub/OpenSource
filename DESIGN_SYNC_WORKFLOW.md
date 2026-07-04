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

The generated XML/XMI must match the Enterprise Architect reference file:

```text
C:\Users\User\git\Seat\EA\voltage_fail_ea_design.xmi
```

That reference is the contract for the generated `design/UnitDesign.xmi`.

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
   - Creates Enterprise Architect compatible XMI in the same shape as `Seat/EA/voltage_fail_ea_design.xmi`.
   - The root element must be `xmi:XMI`, not a bare `uml:Model`.
   - Uses UML/XMI 2.1 namespaces:
     - `xmlns:xmi="http://schema.omg.org/spec/XMI/2.1"`
     - `xmlns:uml="http://schema.omg.org/spec/UML/2.1"`
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
   - `scripts/post-commit`: hook for commits made inside the `process` repository.
   - `scripts/seat-post-commit`: hook for commits in the parent repository that change `Seat/` C/C++ files.
   - `scripts/install_git_hook.ps1`: installs the process-local hook.
   - `scripts/install_seat_hook.ps1`: installs the parent-repository Seat watcher hook.
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

Install the Seat watcher hook in the parent repository:

```powershell
cd C:\Users\User\git
powershell -ExecutionPolicy Bypass -File process\scripts\install_seat_hook.ps1
```

The Seat watcher detects C/C++ files changed under `Seat/` in the latest commit and invokes:

```powershell
python process\agents\pipeline.py --root process <changed Seat files>
```

## EA-Compatible XML Generation Contract

`design/UnitDesign.xmi` must be generated in the same structural style as `Seat/EA/voltage_fail_ea_design.xmi`.

### Required Root Structure

The output root must be:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xmi:XMI xmi:version="2.1"
    xmlns:xmi="http://schema.omg.org/spec/XMI/2.1"
    xmlns:uml="http://schema.omg.org/spec/UML/2.1">
  <uml:Model xmi:id="model_voltage_fail" name="VoltageFail_SW_Design">
    <packagedElement xmi:type="uml:Package" xmi:id="pkg_voltage_fail" name="VoltageFail">
      ...
    </packagedElement>
  </uml:Model>
</xmi:XMI>
```

Do not generate a bare `<uml:Model>` root for EA import.

### Required Top-Level Elements

Inside package `VoltageFail`, generate these elements in this order:

1. `uml:Enumeration` named `VoltageFail_OutputSignalType`
2. `uml:DataType` named `VoltageFail_ParamsType`
3. `uml:DataType` named `VoltageFail_InputType`
4. `uml:DataType` named `VoltageFail_StateType`
5. `uml:DataType` named `VoltageFail_OutputType`
6. `uml:Component` named `VoltageFail Component`
7. `uml:Class` named `VoltageFail`
8. `uml:Package` named `Requirements`
9. `uml:Activity` named `VoltageFail_Update Activity`
10. `uml:StateMachine` named `Voltage Fail Latch State Machine`
11. `uml:Class` named `Output_INT_VoltageFail Decision Table`

### AST to EA XMI Mapping

Map C `typedef enum` to `uml:Enumeration`.

```xml
<packagedElement xmi:type="uml:Enumeration" xmi:id="enum_output_signal" name="VoltageFail_OutputSignalType">
  <ownedLiteral xmi:id="enum_lit_off" name="VOLTAGE_FAIL_OUTPUT_OFF"/>
</packagedElement>
```

Map C `typedef struct` to `uml:DataType`, not `uml:Class`.

```xml
<packagedElement xmi:type="uml:DataType" xmi:id="dt_params" name="VoltageFail_ParamsType">
  <ownedAttribute xmi:id="attr_param_high_det" name="Par_HighVoltageDetection"/>
</packagedElement>
```

Map C functions to `ownedOperation` under class `VoltageFail`, not top-level `uml:Operation`.

```xml
<packagedElement xmi:type="uml:Class" xmi:id="class_voltage_fail" name="VoltageFail">
  <ownedOperation xmi:id="op_init" name="VoltageFail_Init">
    <ownedParameter xmi:id="param_init_state" name="state" direction="inout"/>
  </ownedOperation>
</packagedElement>
```

Static helper functions must be private operations:

| C function | EA operation visibility |
| --- | --- |
| `VoltageFail_AddSaturated` | `private` |
| `VoltageFail_UpdateFilter` | `private` |
| `VoltageFail_GetOutput` | `private` |

Public API functions omit `visibility` unless the generator has an explicit reason to write `public`:

| C function | Parameter direction rules |
| --- | --- |
| `VoltageFail_Init` | `state` is `inout` |
| `VoltageFail_Update` | `state` is `inout`, `params` is `in`, `input` is `in`, `elapsedMs` is `in`, `output` is `out` |

### Required Design Enrichment

The generator must preserve or regenerate EA design information that is not directly available from AST:

| Element | Required content source |
| --- | --- |
| `VoltageFail Component` | Component comment describing voltage failure detection, filtering, and hysteresis. |
| `Requirements` package | Requirement classes `VF-R-001` through `VF-R-009`. |
| `VoltageFail_Update Activity` | Comment describing update flow: pointer validation, high/low filters, hysteresis, output copy, output calculation. |
| `Voltage Fail Latch State Machine` | Region with states `Off`, `On`, transitions `DetectionFilterReached`, `ReturnThresholdReached`. |
| `Output_INT_VoltageFail Decision Table` | Comment describing output priority: invalid config, over voltage, low voltage, off. |

### Stable ID Rules

For the `VoltageFail` module, use EA-readable stable IDs that match the reference style:

| Element | ID |
| --- | --- |
| Model | `model_voltage_fail` |
| Package | `pkg_voltage_fail` |
| Requirements package | `pkg_requirements` |
| Component | `cmp_voltage_fail` |
| Main class | `class_voltage_fail` |
| Params datatype | `dt_params` |
| Input datatype | `dt_input` |
| State datatype | `dt_state` |
| Output datatype | `dt_output` |
| Output enum | `enum_output_signal` |
| Activity | `act_voltage_fail_update` |
| State machine | `sm_fail_latch` |
| Decision table | `class_output_decision_table` |

Generated IDs for attributes, literals, parameters, and comments should remain stable across runs. Prefer semantic IDs such as `attr_state_high_vbat`, `op_update`, and `comment_req_vf_001` over hash IDs.

### Do Not Generate

Do not generate these current MVP shapes for EA target output:

- `<uml:Model ...>` as the document root
- `xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML"` for this EA-compatible output
- C structs as `uml:Class`
- C functions as package-level `uml:Operation`
- Hash-only `xmi:id` values when a semantic ID is known

## Enterprise Architect Import

Import these files in EA:

1. `design/Architecture.xmi`
2. `design/UnitDesign.xmi`

Use `File > Import > Import Package from XMI`, then save the EA project as `.qea`.
