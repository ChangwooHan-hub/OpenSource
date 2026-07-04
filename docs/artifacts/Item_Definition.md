# Item Definition: Voltage Fail Detection Component

**Artifact ID:** ART-ITEM-001
**Project ID:** PRJ-EPB-001
**Status:** Approved
**Version:** 1.0

## 1. 아이템 목적 (Item Purpose)
Voltage Fail Detection 컴포넌트는 차량의 메인 배터리(VBAT)와 점화 전원(IGN1) 입력 전압을 실시간으로 모니터링하여, 전압이 정상 동작 범위를 벗어날 경우(과전압 또는 저전압) 시스템에 페일 세이프(Fail-Safe) 상태를 알리는 역할을 수행합니다.

## 2. 기능 설명 (Function Description)
- **High Voltage Detection (과전압 감지):** VBAT 또는 IGN1 전압이 임계값 이상으로 지속될 경우 `OVER_VOLTAGE` 상태를 출력합니다.
- **Low Voltage Detection (저전압 감지):** VBAT 또는 IGN1 전압이 임계값 이하로 지속될 경우 `LOW_VOLTAGE` 상태를 출력합니다.
- **Filtering & Hysteresis (필터링 및 히스테리시스):** 일시적인 전압 노이즈로 인한 오동작을 방지하기 위해 필터링 타임을 적용하며, 복귀(Return) 시에는 히스테리시스를 적용합니다.

## 3. 시스템 경계 (System Boundary)
- **입력:** 하드웨어 추상화 계층(HAL)으로부터 전달받는 ADC 변환 전압 값 (`Input_H_VBAT`, `Input_H_IGN1`) 및 팩토리 모드 상태.
- **출력:** 애플리케이션 소프트웨어(ASW)의 모터 제어 및 경고등 로직으로 전달되는 통합 전압 상태 (`Output_INT_VoltageFail`).

## 4. 안전 및 보안 가정 (Safety & Security Assumptions)
- 입력되는 ADC 값은 하드웨어 고장(단선, 단락)을 이미 1차적으로 필터링한 신뢰할 수 있는 디지털 값이라고 가정합니다. (안전)
- CAN/LIN 네트워크를 통한 외부 제어 명령이 해당 모듈의 파라미터 임계값을 임의로 변경할 수 없도록 E2E 보호 및 접근 제어가 적용되어 있다고 가정합니다. (보안)
