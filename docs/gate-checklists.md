# 게이트 체크리스트

## 1. 공통 게이트 판정 규칙

게이트는 `Pass`, `Conditional Pass`, `Fail` 중 하나로 판정한다.

| 판정 | 기준 |
|---|---|
| Pass | 모든 필수 산출물이 승인되었고, 차단 이슈가 없으며, 필수 추적성이 충족됨 |
| Conditional Pass | 경미한 미완료 항목이 있으나 승인권자가 조치 기한과 책임자를 지정함 |
| Fail | 필수 산출물 누락, 중대 이슈, 미승인 리스크, 핵심 추적성 누락 중 하나 이상 존재 |

## 2. 공통 체크 항목

모든 게이트는 아래 공통 항목을 포함한다.

| Check ID | 항목 | Pass 기준 | 차단 여부 |
|---|---|---|---|
| GC-COM-001 | 필수 산출물 존재 | 해당 게이트의 Required 산출물이 모두 생성됨 | Yes |
| GC-COM-002 | 산출물 승인 상태 | Required 산출물이 Approved 또는 Baselined 상태 | Yes |
| GC-COM-003 | 오픈 이슈 | Severity High 이상 오픈 이슈 없음 | Yes |
| GC-COM-004 | 변경 영향 분석 | 해당 단계 변경 요청에 대한 영향 분석 완료 | Yes |
| GC-COM-005 | 추적성 누락 | 필수 상하위 링크 누락 없음 | Yes |
| GC-COM-006 | 역할 승인 | 필수 승인자 전원 승인 | Yes |
| GC-COM-007 | 조건부 승인 항목 | 조건부 승인 항목의 책임자와 기한 지정 | No |

## 3. G0 Project Kickoff

목적: 프로젝트 범위, 적용 표준, 역할, 개발 방법, 테일러링 기준을 확정한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G0-001 | 프로젝트 범위 정의 | 개발 대상, 제외 범위, 고객/내부 목적 명시 | Project Plan |
| GC-G0-002 | 표준 적용 범위 | ASPICE, ISO 26262, ISO/SAE 21434 적용 수준 명시 | Process Tailoring Plan |
| GC-G0-003 | 역할과 책임 | PM, Safety, Cybersecurity, QA, Verification 역할 지정 | Project Plan |
| GC-G0-004 | 일정과 게이트 | G0~G7 일정과 승인권자 정의 | Project Plan |
| GC-G0-005 | 형상/변경관리 | 저장소, 기준선, 변경 요청 절차 정의 | Configuration Management Plan |

## 4. G1 Item Definition Review

목적: 개발 대상과 시스템 경계, 운용 시나리오, 이해관계자 요구를 확정한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G1-001 | Item Definition | 기능, 경계, 외부 인터페이스, 운용 환경 포함 | Item Definition |
| GC-G1-002 | 이해관계자 요구 | 고객/법규/시스템 요구가 식별됨 | Stakeholder Requirement |
| GC-G1-003 | 안전 범위 | 안전 관련 기능과 오용 시나리오 후보 정의 | Safety Plan, Item Definition |
| GC-G1-004 | 보안 범위 | 자산, 신뢰 경계, 통신 인터페이스 후보 정의 | Cybersecurity Plan, Item Definition |
| GC-G1-005 | 추적성 시작점 | Stakeholder Need에서 Item까지 링크 생성 | Traceability Matrix |

## 5. G2 Risk Analysis Review

목적: HARA/TARA를 통해 안전/보안 리스크와 목표를 확정한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G2-001 | HARA 완료 | Hazard, Operational Situation, S/E/C, ASIL 결정 | HARA |
| GC-G2-002 | Safety Goal | ASIL QM 초과 항목에 Safety Goal 생성 | Safety Goal List |
| GC-G2-003 | TARA 완료 | Asset, Damage Scenario, Threat Scenario, Risk 결정 | TARA |
| GC-G2-004 | Cybersecurity Goal | 허용 불가 보안 리스크에 목표 생성 | Cybersecurity Goal List |
| GC-G2-005 | 리스크 수용 | 잔여 또는 보류 리스크의 승인권자 명시 | Risk Acceptance Record |
| GC-G2-006 | 목표 추적성 | Hazard/Threat에서 Goal까지 링크 완성 | Traceability Matrix |

## 6. G3 Requirement Baseline

목적: 시스템, SW, 안전, 보안 요구사항을 기준선으로 확정한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G3-001 | 시스템 요구사항 | 완전성, 일관성, 검증가능성 검토 완료 | System Requirement Specification |
| GC-G3-002 | SW 요구사항 | 시스템 요구사항에서 SW 요구사항 도출 완료 | Software Requirement Specification |
| GC-G3-003 | 안전 요구사항 | Safety Goal에서 안전 요구사항 도출 완료 | Safety Requirement Specification |
| GC-G3-004 | 보안 요구사항 | Cybersecurity Goal에서 보안 요구사항 도출 완료 | Cybersecurity Requirement Specification |
| GC-G3-005 | 요구사항 품질 | TBD/TBC 없음, 중복/충돌 항목 처리 완료 | Requirement Review Report |
| GC-G3-006 | 요구사항 추적성 | Goal -> System Req -> SW Req 링크 완성 | Traceability Matrix |

## 7. G4 Architecture Review

목적: 요구사항을 만족하는 시스템/SW 아키텍처와 안전/보안 컨셉을 확정한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G4-001 | 시스템 아키텍처 | 기능 블록, 인터페이스, 배치 구조 정의 | System Architecture Description |
| GC-G4-002 | SW 아키텍처 | 컴포넌트, 인터페이스, 런타임 구조 정의 | Software Architecture Description |
| GC-G4-003 | 안전 컨셉 | Safety Mechanism, FFI, ASIL 분해 근거 정의 | Technical Safety Concept |
| GC-G4-004 | 보안 컨셉 | 보안 메커니즘, 신뢰 경계, 자산 보호 설계 정의 | Cybersecurity Concept |
| GC-G4-005 | 요구사항 할당 | 요구사항이 아키텍처 요소에 할당됨 | Traceability Matrix |
| GC-G4-006 | 분석 결과 | FMEA/FTA/STPA 또는 위협 완화 분석 기록 | Safety/Security Analysis Report |

## 8. G5 Implementation Readiness

목적: 상세설계와 구현/검증 준비 상태를 확인한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G5-001 | 상세설계 | SW 컴포넌트별 상세설계 완료 | Detailed Design Specification |
| GC-G5-002 | 코딩 규칙 | MISRA, CERT-C 등 적용 규칙 정의 | Coding Guideline |
| GC-G5-003 | 단위 테스트 계획 | 단위 테스트 범위와 커버리지 목표 정의 | Unit Test Specification |
| GC-G5-004 | 정적분석 계획 | 정적분석 도구, 규칙, 예외 처리 기준 정의 | Static Analysis Plan |
| GC-G5-005 | 설계 추적성 | SW Req -> Design -> Unit Test 링크 완성 | Traceability Matrix |

## 9. G6 Integration & Verification Review

목적: 구현, 통합, 검증 결과가 요구사항과 안전/보안 목표를 만족하는지 확인한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G6-001 | 구현 완료 | 기준선 대상 코드 모듈 구현 완료 | Source Baseline Record |
| GC-G6-002 | 정적분석 | 차단 등급 위반 없음 또는 승인된 예외 존재 | Static Analysis Report |
| GC-G6-003 | 단위 테스트 | 필수 테스트 통과, 커버리지 목표 충족 | Unit Test Report |
| GC-G6-004 | 통합 테스트 | 주요 인터페이스와 오류 처리 검증 완료 | Integration Test Report |
| GC-G6-005 | 시스템 검증 | 시스템 요구사항 검증 결과 확보 | System Verification Report |
| GC-G6-006 | 안전 검증 | Safety Requirement 검증 증거 확보 | Safety Verification Report |
| GC-G6-007 | 보안 검증 | Security Requirement 검증 증거 확보 | Cybersecurity Verification Report |
| GC-G6-008 | 테스트 추적성 | Req -> Test Case -> Test Result 링크 완성 | Traceability Matrix |

## 10. G7 Release Readiness

목적: 릴리즈 가능 여부를 최종 승인한다.

| Check ID | 항목 | Pass 기준 | 필수 산출물 |
|---|---|---|---|
| GC-G7-001 | 릴리즈 범위 | 릴리즈 대상 형상과 버전 확정 | Release Note |
| GC-G7-002 | 미해결 이슈 | 차단 이슈 없음, 잔여 이슈 승인 완료 | Issue Summary |
| GC-G7-003 | 잔여 리스크 | 안전/보안 잔여 리스크 승인 완료 | Risk Acceptance Record |
| GC-G7-004 | Safety Case | 안전 주장, 근거, 증거 연결 완료 | Safety Case |
| GC-G7-005 | Cybersecurity Case | 보안 주장, 근거, 증거 연결 완료 | Cybersecurity Case |
| GC-G7-006 | 최종 추적성 | Hazard/Threat부터 Evidence까지 필수 링크 완성 | Traceability Matrix |
| GC-G7-007 | 릴리즈 승인 | PM, QA, Safety, Cybersecurity 승인 완료 | Release Approval Report |

