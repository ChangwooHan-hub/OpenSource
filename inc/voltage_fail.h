#ifndef VOLTAGE_FAIL_H
#define VOLTAGE_FAIL_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    VOLTAGE_FAIL_OUTPUT_OFF = 0,
    VOLTAGE_FAIL_OUTPUT_LOW_VOLTAGE = 1,
    VOLTAGE_FAIL_OUTPUT_OVER_VOLTAGE = 2,
    VOLTAGE_FAIL_OUTPUT_INVALID_CONFIG = 3
} VoltageFail_OutputSignalType;

typedef struct {
    uint16_t Par_HighVoltageDetection;
    uint16_t Par_HighVoltageFailFiltering;
    uint16_t Par_LowVoltageDetection;
    uint16_t Par_LowVoltageFailFiltering;
    uint16_t Par_HighVoltageReturn;
    uint16_t Par_LowVoltageReturn;
    uint16_t Par_ExhibitionLowVoltageReturn;
} VoltageFail_ParamsType;

typedef struct {
    uint16_t Input_H_VBAT;
    uint16_t Input_H_IGN1;
    bool Input_C_FactoryMode;
} VoltageFail_InputType;

typedef struct {
    bool m_VoltageHighFail;
    bool m_VoltageHighFail_IGN1;
    bool m_VoltageLowFail;
    bool m_VoltageLowFail_IGN1;
    uint32_t highVbatFilterTimeMs;
    uint32_t highIgn1FilterTimeMs;
    uint32_t lowVbatFilterTimeMs;
    uint32_t lowIgn1FilterTimeMs;
} VoltageFail_StateType;

typedef struct {
    bool m_VoltageHighFail;
    bool m_VoltageHighFail_IGN1;
    bool m_VoltageLowFail;
    bool m_VoltageLowFail_IGN1;
    VoltageFail_OutputSignalType Output_INT_VoltageFail;
} VoltageFail_OutputType;

void VoltageFail_Init(VoltageFail_StateType* state);

void VoltageFail_Update(
    VoltageFail_StateType* state,
    const VoltageFail_ParamsType* params,
    const VoltageFail_InputType* input,
    uint32_t elapsedMs,
    VoltageFail_OutputType* output
);

#endif // VOLTAGE_FAIL_H
