# System Requirement Specification (SRS)

**Artifact ID:** ART-SRS-001
**Project ID:** PRJ-EPB-001
**Status:** Approved
**Version:** 1.0

## 1. 기능 요구사항 (Functional Requirements)
- **REQ-SYS-001:** 시스템은 IGN1과 VBAT의 전압을 밀리초(ms) 단위로 주기적으로 모니터링해야 한다.
- **REQ-SYS-002:** 전압이 설정된 임계값(Par_HighVoltageDetection) 이상인 상태가 일정 시간(Par_HighVoltageFailFiltering) 유지되면 과전압 페일 상태로 판단해야 한다. (관련: VF-R-001, VF-R-002)

## 2. 안전 요구사항 (Safety Requirements)
- **REQ-SAF-001 [ASIL D]:** 시스템은 노이즈로 인한 페일 상태 플리커링(Flickering)을 막기 위해, 정상 전압으로 복귀 시 히스테리시스 임계값(Par_HighVoltageReturn 등)을 적용해야 한다. (관련: SG-003, VF-R-005, VF-R-006)
- **REQ-SAF-002 [ASIL D]:** 과전압과 저전압이 동시에 탐지되는 논리적 모순 상태(센서/회로 고장 의심) 발생 시, 시스템은 `INVALID_CONFIG` 오류 코드를 출력해야 한다. (관련: VF-R-009)

## 3. 인터페이스 요구사항 (Interface Requirements)
- **REQ-INT-001:** 전압 평가의 최종 결과는 `VoltageFail_OutputSignalType` 열거형으로 제공되며, 상태값은 `OFF`, `LOW_VOLTAGE`, `OVER_VOLTAGE`, `INVALID_CONFIG`로 구분된다.
