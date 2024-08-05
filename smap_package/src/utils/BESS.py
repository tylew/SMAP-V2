class BESS:
    def __init__(self,soc_max=300, soc_min=0,peak_charge_rate=-150,peak_discharge_rate=150,eta_charge=0.948,eta_discharge=0.948,initial_soc=0):
        self.soc_max = soc_max
        self.soc_min = soc_min
        self.peak_charge_rate = peak_charge_rate
        self.peak_discharge_rate = peak_discharge_rate
        self.eta_charge = eta_charge
        self.eta_discharge = eta_discharge
        self.initial_soc = initial_soc