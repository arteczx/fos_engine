class Units:
    # Length
    MM_TO_M = 0.001
    M_TO_MM = 1000.0
    INCH_TO_M = 0.0254
    M_TO_INCH = 39.3701

    # Pressure
    PSI_TO_PA = 6894.76
    PA_TO_PSI = 1.0 / 6894.76
    BAR_TO_PA = 100000.0
    PA_TO_BAR = 0.00001

    # Density
    G_CM3_TO_KG_M3 = 1000.0
    KG_M3_TO_G_CM3 = 0.001

    # Force
    LBF_TO_N = 4.44822
    N_TO_LBF = 0.224809

    @staticmethod
    def mm_to_m(mm):
        return mm * Units.MM_TO_M

    @staticmethod
    def m_to_mm(m):
        return m * Units.M_TO_MM

    @staticmethod
    def psi_to_pa(psi):
        return psi * Units.PSI_TO_PA

    @staticmethod
    def pa_to_psi(pa):
        return pa * Units.PA_TO_PSI

    @staticmethod
    def g_cm3_to_kg_m3(rho):
        return rho * Units.G_CM3_TO_KG_M3

    @staticmethod
    def kg_m3_to_g_cm3(rho):
        return rho * Units.KG_M3_TO_G_CM3
