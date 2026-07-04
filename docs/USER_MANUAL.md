# 프로세스 자동화 파이프라인 사용자 매뉴얼 (SDR/SAR Agent)

본 매뉴얼은 C/C++ 소스코드 변경을 감지하여 소프트웨어 설계(Unit Design)와 아키텍처(Architecture)의 일관성을 검토하고, 프로세스 규제(ASPICE, ISO 26262, ISO/SAE 21434) 산출물과 추적성을 자동으로 업데이트하는 **AI 자동화 파이프라인**의 사용법을 안내합니다.

---

## 1. 시스템 개요

개발자가 C/C++ 코드를 Git에 커밋하면, 백그라운드에서 다음 작업이 자동으로 수행됩니다.

1. **AST Parser**: 변경된 코드의 구조(클래스, 함수, 구조체, 의존성) 추출
2. **SDR Agent (단위 설계 검토)**: 추출된 코드 구조를 바탕으로 `UnitDesign.xmi` 업데이트 및 단위 설계 리뷰 리포트 생성
3. **SAR Agent (아키텍처 리뷰)**: `UnitDesign.xmi`와 `Architecture.xmi`를 비교하여 레이어 위반, 등록되지 않은 컴포넌트 등 아키텍처 규칙 위반 탐지
4. **Process Integrator**: AI 에이전트의 결과물과 이슈를 프로세스 데이터베이스(`project_database.yaml`)에 기록
5. **Dashboard Generator**: 요구사항 - 설계 - 이슈 간의 추적성을 보여주는 시각화 대시보드(`dashboard.html`) 최신화

---

## 2. 초기 설정 및 설치 (Getting Started)

### 2.1 사전 요구 사항
- Python 3.8 이상
- Git
- (선택) Enterprise Architect (XMI 다이어그램 확인용)

### 2.2 패키지 설치
리포지토리 루트(`process` 폴더)에서 의존성 패키지를 설치합니다.
```powershell
pip install -r requirements.txt
```

### 2.3 OpenAI API Key 설정
LLM(GPT)을 이용한 지능형 코드-설계 분석을 위해 환경변수에 API Key를 등록해야 합니다.
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="your-openai-api-key"
```

### 2.4 Git Hook 설치 (자동화 트리거)
코드를 커밋할 때 파이프라인이 자동으로 실행되도록 Git Hook을 설치합니다.
```powershell
# 현재 process 리포지토리에 적용할 경우
powershell -ExecutionPolicy Bypass -File scripts\install_git_hook.ps1

# (또는) 상위 Seat 리포지토리의 변경을 감지할 경우
powershell -ExecutionPolicy Bypass -File scripts\install_seat_hook.ps1
```

---

## 3. 사용 방법 (Workflow)

### 3.1 일반적인 개발 프로세스
평소와 동일하게 C/C++ 소스코드를 수정하고 Git으로 커밋합니다.

```powershell
git add src/voltage_fail.c
git commit -m "Update voltage fail hysteresis logic"
```

커밋 직후, `post-commit` Hook이 작동하며 콘솔에 다음과 같은 파이프라인 실행 로그가 출력됩니다.
- 변경된 파일 분석
- 단위 설계(UnitDesign.xmi) 갱신
- 아키텍처 위반 사항 점검
- 대시보드(dashboard.html) 재생성

> **팁:** 커밋 없이 수동으로 파이프라인을 실행하고 싶다면 아래 명령어를 사용합니다.
> ```powershell
> python agents\pipeline.py --changed-in-last-commit
> # 또는 특정 파일 직접 지정
> python agents\pipeline.py src\voltage_fail.c inc\voltage_fail.h
> ```

---

## 4. 결과물 확인

### 4.1 추적성 대시보드 (가장 중요)
자동화 파이프라인이 종료된 후, 프로젝트 루트에 있는 **`dashboard.html`** 파일을 웹 브라우저(Chrome, Edge 등)로 엽니다.

- **Traceability Map (추적 맵):** 요구사항(VF-R-XXX)이 어떤 클래스에 연결되어 있고, 해당 설계가 어떤 산출물(리포트)로 문서화되었는지, 발견된 이슈가 무엇인지 Mermaid 그래프로 한눈에 확인 가능합니다.
- **자동 생성 산출물 (Artifacts):** 에이전트가 자동 생성한 리포트 내역.
- **이슈 (Issues):** 아키텍처 위반 사항(예: 의존성 위반, 등록되지 않은 컴포넌트 등)을 확인합니다. 심각도(Severity)가 High인 이슈는 게이트 리뷰 시 블로킹 사유가 됩니다.

### 4.2 생성된 문서(리포트) 확인
아래 경로에 Markdown 형태의 상세 리뷰 리포트가 생성됩니다.
- `design/reports/SDRReport_*.md`: 단위 설계 업데이트 내역 및 AI 요약
- `design/reports/ReviewReport_*.md`: 아키텍처 규칙 위반(Rule Findings) 및 AI 분석 내용

### 4.3 Enterprise Architect (EA) 연동
설계 모델의 그래픽 표현(UML 다이어그램)을 보려면 생성된 XMI 파일을 EA로 임포트합니다.
1. Enterprise Architect 실행
2. `File > Import > Import Package from XMI...` 선택
3. `design/Architecture.xmi` 임포트
4. `design/UnitDesign.xmi` 임포트

---

## 5. 설정 및 커스터마이징

설정 파일인 **`agents/config.yaml`**에서 파이프라인 동작 방식을 수정할 수 있습니다.

```yaml
openai:
  enabled: true          # LLM 분석 켜기/끄기
  sdr_model: gpt-5.2     # 사용할 모델 변경 가능
  sar_model: gpt-5.2

architecture:
  allowed_external_dependencies:
    - std
    - stdint # 허용되는 외부 의존성 목록 관리 (위반 이슈 발생 방지)
```

## 6. 문제 해결 (Troubleshooting)

- **`dashboard.html` 생성 오류 발생 시:**
  터미널 출력에 인코딩 오류가 발생한다면, 최신 업데이트가 반영되었는지 확인하고 수동으로 `python scripts/generate_dashboard.py`를 실행해 보세요.
- **LLM 리포트가 생성되지 않음:**
  `OPENAI_API_KEY` 환경변수가 제대로 설정되었는지 확인합니다. 미설정 시 하드코딩된 규칙 기반(Rule-based) 분석만 수행됩니다.
- **Hook을 일시적으로 끄고 커밋하고 싶을 때:**
  환경변수에 `DISABLE_DESIGN_HOOK=1`을 설정하고 커밋합니다.
