# ASPICE, Functional Safety, Cybersecurity Process Demo

이 폴더는 ASPICE, ISO 26262 기능안전, ISO/SAE 21434 사이버보안 활동을 하나의 개발 프로세스로 통합하기 위한 데모 프로그램의 기준 정의서이다.

## 문서 구성

- [통합 프로세스 맵](./process-map.md)
- [게이트 체크리스트](./gate-checklists.md)
- [산출물 템플릿 목록](./artifact-templates.md)
- [데이터 모델](./data-model.md)

## 데모 프로그램 목표

데모 프로그램은 자동차 ECU 또는 임베디드 제어 SW 개발을 가정하고, 다음 기능을 제공한다.

- 개발 단계별 필수 활동과 산출물 안내
- ASPICE, 기능안전, 사이버보안 산출물의 상태 관리
- HARA/TARA 기반 리스크 항목과 요구사항 연결
- 요구사항, 설계, 구현, 테스트, 증거자료 간 추적성 관리
- 게이트별 진입/종료 조건 자동 점검
- Gate Review Report, Traceability Matrix, Safety Case, Cybersecurity Case 초안 생성

## 핵심 원칙

1. 세 표준을 병렬 문서 체계로 분리하지 않고 하나의 개발 흐름에 통합한다.
2. 각 산출물은 명확한 ID, 소유자, 상태, 버전, 승인 이력을 가진다.
3. 게이트는 단순 체크리스트가 아니라 산출물 상태, 추적성, 리스크, 테스트 결과를 함께 평가한다.
4. 데모 프로그램의 모든 화면과 리포트는 데이터 모델의 엔티티에서 생성 가능해야 한다.

