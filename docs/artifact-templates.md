# 산출물 템플릿 목록

## 1. 공통 메타데이터

모든 산출물 템플릿은 아래 메타데이터를 포함한다.

```yaml
artifact_id: ART-XXX-001
artifact_type: ""
project_id: PRJ-EPB-001
title: ""
version: "0.1"
status: Draft
owner: ""
reviewers: []
approvers: []
standard_area:
  - ASPICE
  - ISO 26262
  - ISO/SAE 21434
related_gate: GATE-G0
related_items: []
related_requirements: []
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
baseline_id: ""
change_request_id: ""
```

## 2. 산출물 카탈로그

| ID | 산출물 | 표준 영역 | 생성 단계 | 관련 게이트 | 우선순위 | 권장 형식 |
|---|---|---|---|---|---|---|
| TPL-001 | Project Plan | ASPICE | P0 | G0 | Must | Markdown |
| TPL-002 | Process Tailoring Plan | ASPICE/공통 | P0 | G0 | Must | Markdown |
| TPL-003 | Safety Plan | ISO 26262 | P0 | G0 | Must | Markdown |
| TPL-004 | Cybersecurity Plan | ISO/SAE 21434 | P0 | G0 | Must | Markdown |
| TPL-005 | Configuration Management Plan | ASPICE | P0 | G0 | Should | Markdown |
| TPL-006 | Item Definition | ISO 26262/21434 | P1 | G1 | Must | Markdown |
| TPL-007 | Stakeholder Requirement | ASPICE | P1 | G1 | Must | Markdown |
| TPL-008 | HARA | ISO 26262 | P2 | G2 | Must | YAML/XLSX |
| TPL-009 | Safety Goal List | ISO 26262 | P2 | G2 | Must | YAML/Markdown |
| TPL-010 | TARA | ISO/SAE 21434 | P2 | G2 | Must | YAML/XLSX |
| TPL-011 | Cybersecurity Goal List | ISO/SAE 21434 | P2 | G2 | Must | YAML/Markdown |
| TPL-012 | Risk Acceptance Record | ISO 26262/21434 | P2/P7 | G2/G7 | Must | Markdown |
| TPL-013 | System Requirement Specification | ASPICE | P3 | G3 | Must | Markdown |
| TPL-014 | Software Requirement Specification | ASPICE | P3 | G3 | Must | Markdown |
| TPL-015 | Safety Requirement Specification | ISO 26262 | P3 | G3 | Must | Markdown |
| TPL-016 | Cybersecurity Requirement Specification | ISO/SAE 21434 | P3 | G3 | Must | Markdown |
| TPL-017 | Requirement Review Report | ASPICE/공통 | P3 | G3 | Should | Markdown |
| TPL-018 | System Architecture Description | ASPICE | P4 | G4 | Must | Markdown |
| TPL-019 | Software Architecture Description | ASPICE | P4 | G4 | Must | Markdown |
| TPL-020 | Technical Safety Concept | ISO 26262 | P4 | G4 | Must | Markdown |
| TPL-021 | Cybersecurity Concept | ISO/SAE 21434 | P4 | G4 | Must | Markdown |
| TPL-022 | Safety/Security Analysis Report | ISO 26262/21434 | P4 | G4 | Should | Markdown |
| TPL-023 | Detailed Design Specification | ASPICE | P5 | G5 | Must | Markdown |
| TPL-024 | Coding Guideline | ASPICE/안전/보안 | P5 | G5 | Should | Markdown |
| TPL-025 | Unit Test Specification | ASPICE | P5 | G5 | Must | Markdown |
| TPL-026 | Static Analysis Plan | ASPICE/안전/보안 | P5 | G5 | Should | Markdown |
| TPL-027 | Static Analysis Report | ASPICE/안전/보안 | P6 | G6 | Should | Markdown |
| TPL-028 | Unit Test Report | ASPICE | P6 | G6 | Must | Markdown |
| TPL-029 | Integration Test Report | ASPICE | P6 | G6 | Must | Markdown |
| TPL-030 | System Verification Report | ASPICE | P6 | G6 | Must | Markdown |
| TPL-031 | Safety Verification Report | ISO 26262 | P6 | G6 | Must | Markdown |
| TPL-032 | Cybersecurity Verification Report | ISO/SAE 21434 | P6 | G6 | Must | Markdown |
| TPL-033 | Traceability Matrix | 공통 | P3~P7 | G3~G7 | Must | YAML/XLSX |
| TPL-034 | Issue Summary | ASPICE/공통 | P6/P7 | G6/G7 | Must | Markdown |
| TPL-035 | Change Request | ASPICE/공통 | 전 단계 | 모든 게이트 | Must | Markdown |
| TPL-036 | Safety Case | ISO 26262 | P7 | G7 | Must | Markdown |
| TPL-037 | Cybersecurity Case | ISO/SAE 21434 | P7 | G7 | Must | Markdown |
| TPL-038 | Gate Review Report | 공통 | 모든 단계 | 모든 게이트 | Must | Markdown |
| TPL-039 | Release Note | 공통 | P7 | G7 | Must | Markdown |
| TPL-040 | Release Approval Report | 공통 | P7 | G7 | Must | Markdown |

## 3. 주요 템플릿 섹션

### 3.1 Project Plan

- 프로젝트 개요
- 적용 표준과 목표 성숙도
- 범위와 제외 범위
- 역할과 책임
- 일정과 게이트
- 리스크 관리 전략
- 산출물 관리 전략
- 검토와 승인 체계

### 3.2 Item Definition

- 아이템 목적
- 기능 설명
- 시스템 경계
- 외부 인터페이스
- 운용 환경
- 운용 시나리오
- 오용 시나리오
- 의존 시스템
- 안전 관련 가정
- 보안 관련 가정

### 3.3 HARA

```yaml
hazards:
  - hazard_id: HAZ-001
    item_id: ITEM-EPB-001
    malfunction: "주행 중 의도치 않은 제동"
    operational_situation: "고속 주행"
    severity: S3
    exposure: E4
    controllability: C3
    asil: D
    safety_goal_id: SG-001
    rationale: ""
    status: Draft
```

### 3.4 TARA

```yaml
threats:
  - threat_id: THR-001
    asset: "Brake Control CAN Message"
    damage_scenario: "위조 메시지로 의도치 않은 제동 발생"
    threat_scenario: "진단 포트 또는 네트워크 접근 후 CAN 메시지 주입"
    impact: High
    attack_feasibility: Medium
    risk_level: High
    cybersecurity_goal_id: CSG-001
    treatment: Mitigate
    status: Draft
```

### 3.5 Requirement Specification

- 요구사항 ID
- 요구사항 문장
- 유형: Functional, Safety, Cybersecurity, Diagnostic, Performance, Interface
- 근거
- 상위 링크
- 하위 링크
- 검증 방법: Review, Analysis, Test, Inspection
- 우선순위
- ASIL/CAL 또는 관련 리스크 등급
- 승인 상태

### 3.6 Architecture Description

- 아키텍처 개요
- 컴포넌트 목록
- 인터페이스 목록
- 데이터/제어 흐름
- 요구사항 할당
- 안전 메커니즘
- 보안 메커니즘
- 독립성/간섭 분석
- 설계 의사결정과 근거

### 3.7 Test Specification

- 테스트 목적
- 테스트 대상 요구사항
- 테스트 환경
- 사전 조건
- 절차
- 입력 데이터
- 기대 결과
- 판정 기준
- 자동화 여부
- 증거자료 링크

### 3.8 Traceability Matrix

```yaml
links:
  - link_id: TRACE-001
    source_type: Hazard
    source_id: HAZ-001
    target_type: SafetyGoal
    target_id: SG-001
    relation: derives
    status: Valid
```

### 3.9 Gate Review Report

- 게이트 ID
- 검토 일자
- 참석자
- 필수 산출물 상태
- 체크리스트 결과
- 추적성 결과
- 미해결 이슈
- 잔여 리스크
- 결정: Pass, Conditional Pass, Fail
- 조건부 승인 조치
- 승인자

### 3.10 Safety Case / Cybersecurity Case

- Case 범위
- 주장 Claim
- 논거 Argument
- 증거 Evidence
- 잔여 리스크
- 미해결 가정
- 승인 기록

## 4. MVP 템플릿 우선순위

초기 데모에서는 아래 템플릿부터 구현한다.

| 순서 | 템플릿 | 이유 |
|---|---|---|
| 1 | Item Definition | HARA/TARA와 요구사항의 공통 입력 |
| 2 | HARA | 기능안전 데모의 핵심 |
| 3 | TARA | 사이버보안 데모의 핵심 |
| 4 | Requirement Specification | ASPICE 추적성의 중심 |
| 5 | Architecture Description | 요구사항 할당과 설계 검토 |
| 6 | Test Specification/Report | 검증 증거 연결 |
| 7 | Traceability Matrix | 게이트 자동 판정의 핵심 데이터 |
| 8 | Gate Review Report | 데모 결과 출력 |
| 9 | Safety Case | 기능안전 최종 주장 |
| 10 | Cybersecurity Case | 사이버보안 최종 주장 |

