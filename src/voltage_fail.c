#include "voltage_fail.h"

static uint32_t VoltageFail_AddSaturated(uint32_t a, uint32_t b) {
    uint32_t c = a + b;
    if (c < a) return UINT32_MAX;
    return c;
}

static void VoltageFail_UpdateFilter(
    bool condition,
    uint32_t* filterTime,
    uint32_t elapsedMs,
    uint16_t thresholdMs,
    bool* latchState
) {
    if (condition) {
        *filterTime = VoltageFail_AddSaturated(*filterTime, elapsedMs);
        if (*filterTime >= thresholdMs) {
            *latchState = true;
        }
    } else {
        *filterTime = 0;
    }
}

static VoltageFail_OutputSignalType VoltageFail_GetOutput(const VoltageFail_StateType* state) {
    bool anyHigh = state->m_VoltageHighFail || state->m_VoltageHighFail_IGN1;
    bool anyLow = state->m_VoltageLowFail && state->m_VoltageLowFail_IGN1;

    if (anyHigh && anyLow) return VOLTAGE_FAIL_OUTPUT_INVALID_CONFIG;
    if (anyHigh) return VOLTAGE_FAIL_OUTPUT_OVER_VOLTAGE;
    if (anyLow) return VOLTAGE_FAIL_OUTPUT_LOW_VOLTAGE;
    
    return VOLTAGE_FAIL_OUTPUT_OFF;
}

void VoltageFail_Init(VoltageFail_StateType* state) {
    state->m_VoltageHighFail = false;
    state->m_VoltageHighFail_IGN1 = false;
    state->m_VoltageLowFail = false;
    state->m_VoltageLowFail_IGN1 = false;
    
    state->highVbatFilterTimeMs = 0;
    state->highIgn1FilterTimeMs = 0;
    state->lowVbatFilterTimeMs = 0;
    state->lowIgn1FilterTimeMs = 0;
}

void VoltageFail_Update(
    VoltageFail_StateType* state,
    const VoltageFail_ParamsType* params,
    const VoltageFail_InputType* input,
    uint32_t elapsedMs,
    VoltageFail_OutputType* output
) {
    // High Voltage Detection
    VoltageFail_UpdateFilter(
        input->Input_H_VBAT >= params->Par_HighVoltageDetection,
        &state->highVbatFilterTimeMs, elapsedMs, params->Par_HighVoltageFailFiltering,
        &state->m_VoltageHighFail
    );
    VoltageFail_UpdateFilter(
        input->Input_H_IGN1 >= params->Par_HighVoltageDetection,
        &state->highIgn1FilterTimeMs, elapsedMs, params->Par_HighVoltageFailFiltering,
        &state->m_VoltageHighFail_IGN1
    );

    // Low Voltage Detection
    VoltageFail_UpdateFilter(
        input->Input_H_VBAT <= params->Par_LowVoltageDetection,
        &state->lowVbatFilterTimeMs, elapsedMs, params->Par_LowVoltageFailFiltering,
        &state->m_VoltageLowFail
    );
    VoltageFail_UpdateFilter(
        input->Input_H_IGN1 <= params->Par_LowVoltageDetection,
        &state->lowIgn1FilterTimeMs, elapsedMs, params->Par_LowVoltageFailFiltering,
        &state->m_VoltageLowFail_IGN1
    );

    // High Voltage Return
    if (state->m_VoltageHighFail && input->Input_H_VBAT <= params->Par_HighVoltageReturn) {
        state->m_VoltageHighFail = false;
    }
    if (state->m_VoltageHighFail_IGN1 && input->Input_H_IGN1 <= params->Par_HighVoltageReturn) {
        state->m_VoltageHighFail_IGN1 = false;
    }

    // Low Voltage Return
    uint16_t lowReturnThreshold = input->Input_C_FactoryMode ? 
        params->Par_LowVoltageReturn : params->Par_ExhibitionLowVoltageReturn;
        
    if (state->m_VoltageLowFail && input->Input_H_VBAT >= lowReturnThreshold) {
        state->m_VoltageLowFail = false;
    }
    if (state->m_VoltageLowFail_IGN1 && input->Input_H_IGN1 >= lowReturnThreshold) {
        state->m_VoltageLowFail_IGN1 = false;
    }

    // Output Mapping
    output->m_VoltageHighFail = state->m_VoltageHighFail;
    output->m_VoltageHighFail_IGN1 = state->m_VoltageHighFail_IGN1;
    output->m_VoltageLowFail = state->m_VoltageLowFail;
    output->m_VoltageLowFail_IGN1 = state->m_VoltageLowFail_IGN1;
    output->Output_INT_VoltageFail = VoltageFail_GetOutput(state);
}
