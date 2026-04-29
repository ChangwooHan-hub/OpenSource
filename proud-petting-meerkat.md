# SDR_Agent / SAR_Agent 기반 소프트웨어 설계 자동화 워크플로우

## Context
C/C++ 소스 코드 변경을 감지하여 Claude LLM 기반 에이전트가 자동으로
소프트웨어 단위 설계(SDR_Agent)와 아키텍처 일관성(SAR_Agent)을 검토·업데이트하고,
결과를 Enterprise Architect에서 읽을 수 있는 XMI 파일로 출력하는 시스템.

---

## 전체 워크플로우 개요

```
[1] 요구사항 분석
    └─ SRS(Software Requirements Spec) 문서 생성

[2] 아키텍처 설계
    └─ Architecture.xmi  (Component, Package, Interface 다이어그램)

[3] 소프트웨어 단위 상세 설계
    └─ UnitDesign.xmi  (Class, Sequence, State 다이어그램)

[4] 소스 코드 (C/C++)
    └─ git commit / push

         ↓ 변경 감지 (git hook)

[5] SDR_Agent
    ├─ C/C++ AST 파싱 (libclang)
    ├─ Claude API로 설계 문서 업데이트
    └─ UnitDesign.xmi 갱신

         ↓ 완료 후 자동 트리거

[6] SAR_Agent
    ├─ Architecture.xmi + UnitDesign.xmi 비교
    ├─ Claude API로 아키텍처 일관성 검토
    ├─ 검토 보고서 생성
    └─ Architecture.xmi 갱신 (필요시)

         ↓

[7] XMI → Enterprise Architect 임포트
    └─ EA: File > Import > Import Package from XMI
```

---

## 컴포넌트 상세 설계

### 컴포넌트 1: Code Change Detector
**역할**: 소스 코드 변경을 감지하고 파이프라인 트리거

| 항목 | 내용 |
|------|------|
| 구현 방식 | git post-commit hook 또는 CI 파이프라인 webhook |
| 입력 | git diff (변경된 .c/.cpp/.h 파일 목록) |
| 출력 | 변경 파일 경로 → SDR_Agent에 전달 |
| 기술 | bash script 또는 Python watchdog |

### 컴포넌트 2: C/C++ AST Parser
**역할**: 소스 코드 구조를 UML 요소로 추출

| 항목 | 내용 |
|------|------|
| 라이브러리 | `libclang` (Python bindings: `clang` 패키지) |
| 추출 대상 | 클래스, 구조체, 함수, 메서드, 멤버변수, 의존성, include 관계 |
| 출력 형식 | 내부 JSON 표현 (→ Claude 컨텍스트로 전달) |

```python
# 추출 요소 예시
{
  "file": "motor_controller.cpp",
  "classes": [
    {
      "name": "MotorController",
      "methods": ["init()", "setSpeed(int)", "stop()"],
      "members": ["int speed_", "bool running_"],
      "dependencies": ["Sensor", "Logger"]
    }
  ],
  "functions": [...],
  "includes": ["sensor.h", "logger.h"]
}
```

### 컴포넌트 3: SDR_Agent (Software Design Review Agent)
**역할**: 변경된 코드를 분석하여 소프트웨어 단위 설계 문서 업데이트

| 항목 | 내용 |
|------|------|
| 모델 | claude-sonnet-4-6 (또는 claude-opus-4-7 for 복잡한 분석) |
| 트리거 | Code Change Detector로부터 변경 파일 수신 |
| 입력 | AST 파싱 결과 JSON + 기존 UnitDesign.xmi |
| 처리 | 변경된 클래스/함수를 XMI 요소로 매핑, 추가/수정/삭제 |
| 출력 | 갱신된 UnitDesign.xmi |

**Claude 프롬프트 구조**:
```
System: 당신은 C/C++ 소프트웨어 설계 전문가입니다.
        주어진 코드 변경사항을 분석하여 UML 설계 문서를 업데이트하세요.

User:   [기존 설계 요약]
        [변경된 코드의 AST JSON]
        → 변경된 설계 요소를 XMI 형식으로 출력하세요.
```

**처리 로직**:
1. 기존 XMI에서 변경 대상 요소 식별 (`xmi:id` 기준)
2. Claude로 의미적 변경 분석 (리팩토링 vs 기능 변경 vs 인터페이스 변경)
3. XMI 요소 추가/수정/삭제
4. 변경 이력 주석 추가 (`<!-- Updated by SDR_Agent 2026-04-29 -->`)

### 컴포넌트 4: SAR_Agent (Software Architecture Review Agent)
**역할**: 단위 설계 변경이 아키텍처에 미치는 영향 검토

| 항목 | 내용 |
|------|------|
| 모델 | claude-opus-4-7 (아키텍처 수준 추론 필요) |
| 트리거 | SDR_Agent 완료 후 자동 실행 |
| 입력 | Architecture.xmi + 갱신된 UnitDesign.xmi + 변경 diff |
| 처리 | 레이어 위반, 의존성 방향 역전, 인터페이스 계약 위반 감지 |
| 출력 | ReviewReport.md + 필요시 갱신된 Architecture.xmi |

**검토 항목**:
- [ ] 레이어드 아키텍처 위반 (하위 레이어가 상위 레이어 의존)
- [ ] 순환 의존성 발생
- [ ] 컴포넌트 인터페이스 계약 변경
- [ ] 새로운 컴포넌트 식별 (아키텍처에 미등록된 클래스)
- [ ] 삭제된 컴포넌트가 아키텍처에 여전히 참조됨

### 컴포넌트 5: XMI Generator / Manager
**역할**: 내부 설계 표현을 Enterprise Architect 호환 XMI로 변환

| 항목 | 내용 |
|------|------|
| XMI 표준 | UML 2.5.1 / XMI 2.5 (Eclipse UML2 호환) |
| EA 임포트 | File > Import > Import Package from XMI (*.xml / *.xmi) |
| 스키마 | `xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML"` |

**XMI 파일 구조**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<uml:Model xmi:version="2.1"
  xmlns:xmi="http://www.omg.org/XMI"
  xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML"
  name="SystemModel">

  <!-- Architecture Layer -->
  <packagedElement xmi:type="uml:Package" xmi:id="arch_pkg" name="Architecture">
    <packagedElement xmi:type="uml:Component" xmi:id="comp_motor" name="MotorSubsystem"/>
    <!-- Interface, Dependency, etc. -->
  </packagedElement>

  <!-- Unit Design Layer -->
  <packagedElement xmi:type="uml:Package" xmi:id="unit_pkg" name="UnitDesign">
    <packagedElement xmi:type="uml:Class" xmi:id="cls_motorctrl" name="MotorController">
      <ownedAttribute xmi:id="attr_speed" name="speed_" type="int"/>
      <ownedOperation xmi:id="op_setspeed" name="setSpeed">
        <ownedParameter name="value" direction="in"/>
      </ownedOperation>
    </packagedElement>
  </packagedElement>

</uml:Model>
```

---

## 데이터 흐름 상세

```
git commit
    │
    ▼
post-commit hook
    │  변경된 파일 목록
    ▼
AST Parser (libclang)
    │  JSON {classes, functions, dependencies}
    ▼
SDR_Agent
    │  기존 UnitDesign.xmi 읽기
    │  Claude API 호출 (변경 분석)
    │  XMI diff 적용
    ▼
UnitDesign.xmi (갱신)
    │
    ▼
SAR_Agent
    │  Architecture.xmi + UnitDesign.xmi 비교
    │  Claude API 호출 (일관성 검토)
    │  ReviewReport.md 생성
    │  (위반 발견 시) Architecture.xmi 갱신 or 경고
    ▼
Output/
  ├── Architecture.xmi   → EA 임포트
  ├── UnitDesign.xmi     → EA 임포트
  └── ReviewReport.md    → 개발자 검토
```

---

## 디렉토리 구조

```
project-root/
├── .git/
│   └── hooks/
│       └── post-commit          # 트리거 스크립트
├── src/                         # C/C++ 소스
├── design/
│   ├── Architecture.xmi         # 아키텍처 XMI (SAR_Agent 관리)
│   ├── UnitDesign.xmi           # 단위 설계 XMI (SDR_Agent 관리)
│   └── reports/
│       └── ReviewReport_YYYYMMDD.md
├── agents/
│   ├── ast_parser.py            # libclang 기반 파서
│   ├── sdr_agent.py             # SDR_Agent 구현
│   ├── sar_agent.py             # SAR_Agent 구현
│   ├── xmi_manager.py           # XMI 읽기/쓰기 유틸리티
│   └── config.yaml              # 모델, 경로, 임계값 설정
└── requirements.txt
```

---

## 기술 스택

| 역할 | 기술 |
|------|------|
| C/C++ 파싱 | `libclang` (Python `clang` 패키지) |
| AI 추론 | Anthropic Claude API (`anthropic` SDK) |
| XMI 처리 | Python `xml.etree.ElementTree` / `lxml` |
| 트리거 | git post-commit hook (bash) |
| 설정 관리 | `PyYAML` |
| 보고서 | Markdown |

---

## Claude API 사용 전략 (프롬프트 캐싱 포함)

```python
# SDR_Agent 호출 예시
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system=[
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}  # 시스템 프롬프트 캐싱
        }
    ],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": existing_xmi_summary,
                    "cache_control": {"type": "ephemeral"}  # 기존 설계 캐싱
                },
                {
                    "type": "text",
                    "text": f"변경사항:\n{ast_diff_json}"
                }
            ]
        }
    ]
)
```

---

## Enterprise Architect 임포트 절차

1. EA 실행
2. `File` > `Import` > `Import Package from XMI...`
3. `Architecture.xmi` 선택 → 아키텍처 패키지 임포트
4. `UnitDesign.xmi` 선택 → 단위 설계 패키지 임포트
5. 다이어그램 자동 생성 또는 EA 내에서 배치

> **참고**: EA 16+ 기준으로 UML2 XMI 포맷 직접 지원.
> .qea 네이티브 저장은 EA 내에서 "Save Project As"로 변환.

---

## 검증 방법 (테스트 시나리오)

| 시나리오 | 기대 결과 |
|----------|-----------|
| 새 클래스 추가 | UnitDesign.xmi에 `uml:Class` 요소 추가됨 |
| 메서드 시그니처 변경 | 해당 `ownedOperation` 업데이트됨 |
| 클래스 삭제 | XMI에서 제거, SAR_Agent가 아키텍처 참조 경고 |
| 레이어 위반 의존성 추가 | SAR_Agent가 ReviewReport에 위반 기록 |
| 아키텍처와 무관한 리팩토링 | XMI 내부 업데이트만, 아키텍처 변경 없음 |

---

## 구현 우선순위 (단계별)

1. **Phase 1** — AST Parser + XMI Manager (기반 인프라)
2. **Phase 2** — SDR_Agent MVP (클래스/함수 변경 반영)
3. **Phase 3** — SAR_Agent MVP (의존성 위반 감지)
4. **Phase 4** — git hook 통합 + 자동화 파이프라인
5. **Phase 5** — EA 임포트 검증 + 보고서 고도화
