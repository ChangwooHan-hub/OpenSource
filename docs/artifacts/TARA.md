# Threat Analysis and Risk Assessment (TARA)

**Artifact ID:** ART-TARA-001
**Project ID:** PRJ-EPB-001
**Status:** Approved
**Version:** 1.0

| Threat ID | Asset (자산) | Damage Scenario (피해 시나리오) | Threat Scenario (위협 시나리오) | Impact | Feasibility | Risk Level | Cybersecurity Goal |
|---|---|---|---|---|---|---|---|
| THR-VF-01 | Voltage Calibration Params | 잘못된 임계값으로 인해 전압 감지 기능 무력화 | 진단 통신(UDS)을 통해 해커가 과/저전압 임계값 파라미터를 임의로 변경 | High | Medium | **High** | CSG-001: 파라미터 변경 시 인증 체계 적용 |
| THR-VF-02 | ADC Input Data | 전압 정상 상태로 위장된 데이터 주입 | 펌웨어 위/변조를 통해 HAL에서 전달되는 전압 값을 항상 정상 범위로 고정 | Severe | Low | **Medium** | CSG-002: 시큐어 부트를 통한 펌웨어 무결성 검증 |

## 도출된 Cybersecurity Goals
- **CSG-001:** 진단 세션을 통한 `VoltageFail_ParamsType` 변경은 반드시 Security Access(인증)를 거친 후 수행되어야 한다.
- **CSG-002:** `VoltageFail_InputType` 데이터는 메모리 보호 영역(MPU/MPU)에 위치하여 비인가된 프로세스의 쓰기 접근을 차단해야 한다.
