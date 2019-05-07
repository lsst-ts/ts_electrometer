from SALPY_Electrometer import *

class DetailedState:
    DisabledState = Electrometer_shared_DetailedState_DisabledState
    EnabledState = Electrometer_shared_DetailedState_EnabledState
    FaultState = Electrometer_shared_DetailedState_FaultState
    OfflineState = Electrometer_shared_DetailedState_OfflineState
    StandbyState = Electrometer_shared_DetailedState_StandbyState
    NotReadingState = Electrometer_shared_DetailedState_NotReadingState
    ConfiguringState = Electrometer_shared_DetailedState_ConfiguringState
    ManualReadingState = Electrometer_shared_DetailedState_ManualReadingState
    ReadingBufferState = Electrometer_shared_DetailedState_ReadingBufferState
    SetDurationReadingState = Electrometer_shared_DetailedState_SetDurationReadingState

class SummaryState:
    DisabledState = Electrometer_shared_SummaryState_DisabledState
    EnabledState = Electrometer_shared_SummaryState_EnabledState
    FaultState = Electrometer_shared_SummaryState_FaultState
    OfflineState = Electrometer_shared_SummaryState_OfflineState
    StandbyState = Electrometer_shared_SummaryState_StandbyState

class UnitToRead:
    Current = Electrometer_shared_UnitToRead_Current
    Charge = Electrometer_shared_UnitToRead_Charge

