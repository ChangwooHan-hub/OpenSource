# Hazard Analysis and Risk Assessment (HARA)

**Artifact ID:** ART-HARA-001
**Project ID:** PRJ-EPB-001
**Status:** Approved
**Version:** 1.0

| Hazard ID | Item | Malfunction (오작동) | Operational Situation (운용 상황) | Severity (S) | Exposure (E) | Controllability (C) | ASIL | Safety Goal |
|---|---|---|---|---|---|---|---|---|
| HAZ-VF-01 | Voltage Fail | 실제 과전압 상태임에도 정상으로 오인하여 모터 구동 허용 | 고속 주행 중 (100km/h 이상) | S3 | E4 | C3 | **ASIL D** | SG-001: 과전압 상태 시 모터 구동을 차단해야 한다. |
| HAZ-VF-02 | Voltage Fail | 실제 저전압 상태임에도 정상으로 오인하여 제동 유지 실패 | 경사로 주차 중 | S2 | E4 | C2 | **ASIL B** | SG-002: 저전압 상태 시 현재 제동력을 유지해야 한다. |
| HAZ-VF-03 | Voltage Fail | 정상 전압 상태임에도 과/저전압으로 오인하여 의도치 않은 제동 해제 발생 | 일반 주행 중 | S3 | E4 | C3 | **ASIL D** | SG-003: 오탐지로 인한 잘못된 제어 모드 진입을 방지해야 한다. |

## 도출된 Safety Goals
- **SG-001 (ASIL D):** 제어기는 배터리 과전압(> 16V) 발생 시, 지정된 필터링 시간 내에 이를 감지하고 시스템을 안전 상태로 전환해야 한다.
- **SG-002 (ASIL B):** 제어기는 배터리 저전압(< 9V) 발생 시, 이를 감지하고 추가적인 전류 소모 동작을 중단해야 한다.
- **SG-003 (ASIL D):** 전압 감지 로직은 노이즈로 인한 오탐지를 방지하기 위해 필터링 및 히스테리시스 로직을 포함해야 한다.
