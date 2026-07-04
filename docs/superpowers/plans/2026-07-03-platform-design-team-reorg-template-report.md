# Platform Design Team Reorg Template Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 2-slide executive report in the provided company template that explains the capability gap created by the reorganization and proposes a platform-design-led response with SW architecture AI support.

**Architecture:** Use template-following mode with the provided `보고 기본 템플릿.pptx` as the only visual source. Duplicate the template slide into a 2-slide starter deck, then edit the copied slides in place with artifact-tool so the company header, footer, logo, title placement, and page markers stay intact while the main body is redesigned into a left-right report layout.

**Tech Stack:** `@oai/artifact-tool`, Node.js, presentation skill template-following scripts, `render_slides.py`, `slides_test.py`

---

### Task 1: Audit The Source Template And Freeze The Slide Map

**Files:**
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-audit.txt`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-frame-map.json`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\deviation-log.txt`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\source-notes.txt`
- Read: `C:\Users\User\Downloads\보고 기본 템플릿.pptx`
- Read: `C:\Users\User\git\process\docs\superpowers\specs\2026-07-03-platform-design-team-reorg-executive-report-design.md`

- [ ] **Step 1: Create the scratch workspace and copy the Korean-named template to an ASCII path**

```powershell
$tmpRoot = & 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' -p "require('node:os').tmpdir()"
$workspace = Join-Path $tmpRoot 'codex-presentations\manual-20260703\template-follow'
$tmpDir = Join-Path $workspace 'tmp'
New-Item -ItemType Directory -Force $workspace,$tmpDir | Out-Null
Copy-Item -LiteralPath 'C:\Users\User\Downloads\보고 기본 템플릿.pptx' -Destination (Join-Path $tmpDir 'template-source.pptx') -Force
```

Expected: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-source.pptx` exists.

- [ ] **Step 2: Inspect the template deck**

```powershell
$env:HOME='C:\Users\User'
$skillDir = 'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations'
$tmpDir = 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  "$skillDir\template_following_scripts\inspect_template_deck.mjs" `
  --workspace $tmpDir `
  --pptx "$tmpDir\template-source.pptx"
```

Expected: the script may exit non-zero in this environment, but it must create inspection artifacts under `$tmpDir\template-inspect\` or write enough render output to examine the template structure.

- [ ] **Step 3: Render the copied template to verify the title/header/footer structure**

```powershell
$env:HOME='C:\Users\User'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations\container_tools\render_slides.py' `
  'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-source.pptx' `
  --output_dir 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-rendered'
```

Expected: `slide-1.png` exists in `template-rendered` and shows the company header bar, title area, page number, and MOBASE ELECTRONICS logo.

- [ ] **Step 4: Write the template audit**

```text
Template source: C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-source.pptx

Observed reusable pattern:
- One blank company-report slide with fixed chrome
- Large title area at top-left
- Fixed "핵심가치(업무태도)" panels at top-right
- Long content canvas in the body
- Bottom-center page number marker
- Bottom-right MOBASE ELECTRONICS logo

Rules to preserve:
- Keep title baseline, horizontal divider, top-right value boxes, page number marker, and logo
- Do not change company colors or chrome
- Fill only the open body canvas
- Use two separate duplicated slides from the same source slide
```

Expected: save the exact text above into `template-audit.txt`.

- [ ] **Step 5: Write the slide mapping**

```json
{
  "outputSlides": [
    {
      "outputSlide": 1,
      "sourceSlide": 1,
      "narrativeRole": "reorganization gap analysis",
      "reuseMode": "duplicate-slide",
      "editTargets": []
    },
    {
      "outputSlide": 2,
      "sourceSlide": 1,
      "narrativeRole": "platform-led response and approval ask",
      "reuseMode": "duplicate-slide",
      "editTargets": []
    }
  ],
  "omittedSourceSlides": []
}
```

Expected: save the exact JSON above into `template-frame-map.json`.

- [ ] **Step 6: Record the allowed deviation**

```text
Slide 1:
- Replace the empty body area with a left-right layout
- Preserve the template chrome, title placement, page number, and logo

Slide 2:
- Replace the empty body area with a left-right layout
- Preserve the template chrome, title placement, page number, and logo
```

Expected: save the exact text above into `deviation-log.txt`.

### Task 2: Build The Starter Deck From The Template

**Files:**
- Read: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-frame-map.json`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter.pptx`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter-preview\slide-1.png`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter-preview\slide-2.png`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter-layout\slide-1.layout.json`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter-layout\slide-2.layout.json`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter-contact-sheet.png`

- [ ] **Step 1: Validate the frame map**

```powershell
$skillDir = 'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations'
$tmpDir = 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  "$skillDir\template_following_scripts\validate_template_plan.mjs" `
  --workspace $tmpDir `
  --map "$tmpDir\template-frame-map.json"
```

Expected: PASS with no JSON validation errors.

- [ ] **Step 2: Duplicate the source slide twice to create the starter deck**

```powershell
$skillDir = 'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations'
$tmpDir = 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  "$skillDir\template_following_scripts\prepare_template_starter_deck.mjs" `
  --workspace $tmpDir `
  --pptx "$tmpDir\template-source.pptx" `
  --map "$tmpDir\template-frame-map.json" `
  --out "$tmpDir\template-starter.pptx" `
  --preview-dir "$tmpDir\template-starter-preview" `
  --layout-dir "$tmpDir\template-starter-layout" `
  --contact-sheet "$tmpDir\template-starter-contact-sheet.png"
```

Expected: `template-starter.pptx` exists and the preview directory contains two starter slides.

- [ ] **Step 3: Render the starter deck for visual confirmation**

```powershell
$env:HOME='C:\Users\User'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations\container_tools\render_slides.py' `
  'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter.pptx' `
  --output_dir 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\starter-rendered'
```

Expected: two rendered slides appear with identical template chrome and empty body space.

### Task 3: Author The Final Deck Edit Script

**Files:**
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\build-platform-template-report.mjs`
- Modify: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\template-starter.pptx`
- Output: `C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx`
- Read: `C:\Users\User\git\process\docs\superpowers\specs\2026-07-03-platform-design-team-reorg-executive-report-design.md`

- [ ] **Step 1: Initialize the artifact-tool workspace**

```powershell
$env:HOME='C:\Users\User'
$skillDir = 'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations'
$tmpDir = 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  "$skillDir\container_tools\setup_artifact_tool_workspace.mjs" `
  --workspace $tmpDir
```

Expected: `$tmpDir\node_modules\@oai\artifact-tool` exists.

- [ ] **Step 2: Create the deck edit script scaffold**

```js
import fs from "node:fs/promises";
import { PresentationFile, FileBlob } from "@oai/artifact-tool";

const sourcePptx = "C:/Users/User/AppData/Local/Temp/codex-presentations/manual-20260703/template-follow/tmp/template-starter.pptx";
const outputPptx = "C:/Users/User/git/process/outputs/platform-design-team-template-report.pptx";

const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePptx));
const slide1 = presentation.slides.items[0];
const slide2 = presentation.slides.items[1];

// Edit duplicated template slides in place here.

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(outputPptx);
```

Expected: save the exact scaffold above into `build-platform-template-report.mjs`.

- [ ] **Step 3: Add slide-1 content blocks to the script**

```js
// Slide 1 title
const slide1Title = slide1.shapes.add({
  geometry: "textbox",
  position: { left: 40, top: 18, width: 610, height: 38 },
  fill: "none",
  line: { style: "solid", fill: "none", width: 0 },
});
slide1Title.text = "조직 개편으로 인한 기능 공백 발생합니다.";
slide1Title.text.style = { fontSize: 32, bold: false, color: "#111111", typeface: "Malgun Gothic" };

// Body summary
const slide1Summary = slide1.shapes.add({
  geometry: "textbox",
  position: { left: 42, top: 62, width: 760, height: 36 },
  fill: "none",
  line: { style: "solid", fill: "none", width: 0 },
});
slide1Summary.text = "아이템 책임 강화는 맞는 방향이지만, 기능조직 해체로 표준·전문성·프로세스 연결고리가 필요합니다.";
slide1Summary.text.style = { fontSize: 16, color: "#444444", typeface: "Malgun Gothic" };
```

Expected: the code above is inserted into `build-platform-template-report.mjs` before export.

- [ ] **Step 4: Add slide-1 right-side benefit/gap lists to the script**

```js
const slide1Benefits = slide1.shapes.add({
  geometry: "roundRect",
  position: { left: 832, top: 118, width: 360, height: 220 },
  fill: "#E9F5EA",
  line: { style: "solid", fill: "#8DBA94", width: 1.2 },
  borderRadius: "rounded-xl",
});
slide1Benefits.text = "강화되는 점\n• 아이템별 의사결정 속도 향상\n• 아이템별 책임 주체 명확화\n• 협업 핸드오프 축소\n• 현장 이슈 대응 즉시성 강화\n• 아이템 단위 우선순위 조정 용이\n• 개발 결과 책임감 강화";
slide1Benefits.text.style = {
  fontSize: 15,
  color: "#234A2F",
  typeface: "Malgun Gothic",
  autoFit: "shrinkText",
  insets: { top: 10, right: 16, bottom: 10, left: 16 }
};

const slide1Gaps = slide1.shapes.add({
  geometry: "roundRect",
  position: { left: 832, top: 356, width: 360, height: 220 },
  fill: "#FFF0EC",
  line: { style: "solid", fill: "#E0A089", width: 1.2 },
  borderRadius: "rounded-xl",
});
slide1Gaps.text = "발생하는 공백\n• 기능 전문성 결속 약화\n• 기술 표준 분산 위험 증가\n• 설계 품질 판단 기준 축 약화\n• 프로세스 연결고리 약화\n• 인력 육성 및 기술 전수 체계 약화\n• 플랫폼설계팀 조정 부담 집중";
slide1Gaps.text.style = {
  fontSize: 15,
  color: "#7A2A1B",
  typeface: "Malgun Gothic",
  autoFit: "shrinkText",
  insets: { top: 10, right: 16, bottom: 10, left: 16 }
};
```

Expected: the slide 1 right-hand lists fit without overflow.

- [ ] **Step 5: Add slide-2 title, message, and approval ask to the script**

```js
const slide2Title = slide2.shapes.add({
  geometry: "textbox",
  position: { left: 40, top: 18, width: 780, height: 38 },
  fill: "none",
  line: { style: "solid", fill: "none", width: 0 },
});
slide2Title.text = "플랫폼설계팀 기술리딩과 AI 지원, 개발 과정 점검 수행으로 개편을 성공시키겠습니다.";
slide2Title.text.style = { fontSize: 28, color: "#111111", typeface: "Malgun Gothic" };

const slide2Summary = slide2.shapes.add({
  geometry: "textbox",
  position: { left: 42, top: 62, width: 790, height: 36 },
  fill: "none",
  line: { style: "solid", fill: "none", width: 0 },
});
slide2Summary.text = "플랫폼설계팀과 연구기획팀 역할 강화, 그리고 SW아키텍처실 AI 기술 지원을 통해 공백을 메우겠습니다.";
slide2Summary.text.style = { fontSize: 16, color: "#444444", typeface: "Malgun Gothic" };

const slide2Decision = slide2.shapes.add({
  geometry: "roundRect",
  position: { left: 54, top: 560, width: 1140, height: 84 },
  fill: "#FCE7D3",
  line: { style: "solid", fill: "#D89C5F", width: 1.2 },
  borderRadius: "rounded-xl",
});
slide2Decision.text = "경영층 의사결정 포인트\n• 개편 방향 유지\n• 플랫폼설계팀 기술 리딩 역할 강화\n• 연구기획팀 프로세스 역할 강화\n• SW아키텍처실 AI 기술 지원 활용 승인";
slide2Decision.text.style = {
  fontSize: 16,
  color: "#7A4712",
  typeface: "Malgun Gothic",
  autoFit: "shrinkText",
  insets: { top: 10, right: 18, bottom: 10, left: 18 }
};
```

Expected: slide 2 contains the final executive ask in the bottom band.

### Task 4: Run The Edit Script And Produce The Final PPTX

**Files:**
- Read: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\build-platform-template-report.mjs`
- Create: `C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx`
- Create: `C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx.inspect.ndjson`

- [ ] **Step 1: Execute the edit script**

```powershell
$env:HOME='C:\Users\User'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\build-platform-template-report.mjs'
```

Expected: `C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx` exists.

- [ ] **Step 2: Confirm the file exists and capture its metadata**

```powershell
Get-Item 'C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx' |
  Format-List FullName,Length,LastWriteTime
```

Expected: PowerPoint file metadata prints without errors.

### Task 5: Render, QA, And Fix Before Delivery

**Files:**
- Read: `C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\qa\rendered\slide-1.png`
- Create: `C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\qa\rendered\slide-2.png`

- [ ] **Step 1: Render the final deck**

```powershell
$env:HOME='C:\Users\User'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations\container_tools\render_slides.py' `
  'C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx' `
  --output_dir 'C:\Users\User\AppData\Local\Temp\codex-presentations\manual-20260703\template-follow\tmp\qa\rendered'
```

Expected: `slide-1.png` and `slide-2.png` exist in the QA render folder.

- [ ] **Step 2: Run overflow detection**

```powershell
$env:HOME='C:\Users\User'
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\User\.codex\plugins\cache\openai-primary-runtime\presentations\26.630.12135\skills\presentations\container_tools\slides_test.py' `
  'C:\Users\User\git\process\outputs\platform-design-team-template-report.pptx'
```

Expected: `Test passed. No overflow detected.` If not, shorten copy before resizing fonts.

- [ ] **Step 3: Manually inspect the rendered slides**

```text
Checklist:
- Template title bar, divider, page number, and company logo are still visible
- Slide 1 left diagram fits under the header and does not collide with the template chrome
- Slide 1 right lists each contain 6 bullets and remain readable
- Slide 2 left role structure remains balanced and not connector-heavy
- Slide 2 right AI support block and bottom decision band are readable
- No default placeholder text remains
```

Expected: every item passes before delivery.

- [ ] **Step 4: Commit the final deliverable work**

```bash
git add docs/superpowers/specs/2026-07-03-platform-design-team-reorg-executive-report-design.md
git commit -m "feat: build template-based reorg report"
```

Expected: clean commit capturing the approved report design context if repository policy requires it.
