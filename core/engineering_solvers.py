"""
Multi-Disciplinary Closed-Form Engineering Solvers
Deterministic physics engines for Structural, Electrical, Civil, Geotechnical, and Mechanical disciplines.
"""
import math
from typing import Dict, Any, Tuple, List

class StructuralAISCWindSolver:
    """ASCE 7-16 Wind Pressure & AISC 360-16 LRFD Steel Member Verification"""

    @staticmethod
    def calculate_asce7_wind_pressure(V_mph: float, z_ft: float, Kd: float = 0.85, Kzt: float = 1.0, Ke: float = 1.0) -> Dict[str, float]:
        """ASCE 7-16 Eq. 26.10-1: Velocity Pressure q_z for Exposure C."""
        Kz = 0.85 if z_ft <= 15.0 else 0.98 if z_ft <= 30.0 else 2.01 * (z_ft / 900.0) ** (2.0 / 9.5)
        qz_psf = 0.00256 * Kz * Kzt * Kd * Ke * (V_mph ** 2)
        return {"Kz": round(Kz, 4), "qz_psf": round(qz_psf, 2), "V_mph": V_mph, "z_ft": z_ft}

    @staticmethod
    def verify_w_beam_flexure_lrfd(demand_Mu_ft_kips: float, Fy_ksi: float, Zx_in3: float, phi: float = 0.90) -> Dict[str, Any]:
        """AISC 360-16 Section F2: Plastic moment capacity (phi * Mn) for compact W-shapes."""
        phi_Mn_ft_kips = (phi * Fy_ksi * Zx_in3) / 12.0
        dcr = demand_Mu_ft_kips / phi_Mn_ft_kips
        return {
            "capacity_phi_Mn_ft_kips": round(phi_Mn_ft_kips, 2),
            "demand_Mu_ft_kips": demand_Mu_ft_kips,
            "dcr": round(dcr, 3),
            "is_compliant": dcr <= 1.000
        }

class ElectricalNECSolver:
    """NFPA 70: National Electrical Code (NEC 2023) 3-Phase Feeder & Branch Sizing"""

    @staticmethod
    def calculate_voltage_drop(I_load: float, length_ft: float, V_nominal: float = 480.0, size_awg: str = '4/0', three_phase: bool = True) -> Dict[str, Any]:
        """NEC 210.19(A) / 215.2: Balanced 3-Phase Cu Conductor Voltage Drop (<3% feeder limit)."""
        cmil_table = {'1/0': 105600, '2/0': 133100, '3/0': 167800, '4/0': 211600, '250 kcmil': 250000, '500 kcmil': 500000}
        cmil = cmil_table.get(size_awg, 211600)
        K = 12.9  # Copper resistivity at 75C (ohms-cmil/ft)
        multiplier = math.sqrt(3) if three_phase else 2.0
        v_drop = (multiplier * K * I_load * length_ft) / float(cmil)
        pct_drop = (v_drop / V_nominal) * 100.0
        return {
            "conductor": f"{size_awg} Cu",
            "v_drop_volts": round(v_drop, 2),
            "pct_drop": round(pct_drop, 2),
            "is_feeder_compliant": pct_drop <= 3.00,
            "is_total_compliant": pct_drop <= 5.00
        }

class GeotechnicalSettlementSolver:
    """Terzaghi 1D Primary Consolidation Settlement (Piecewise NC / OC Clay Layers)"""

    @staticmethod
    def calculate_consolidation(H0_ft: float, e0: float, sigma_v0_psf: float, delta_sigma_psf: float, sigma_p_psf: float, Cc: float = 0.35, Cr: float = 0.05) -> Dict[str, Any]:
        sigma_final = sigma_v0_psf + delta_sigma_psf
        if sigma_p_psf <= sigma_v0_psf:
            Sc_ft = (Cc * H0_ft / (1.0 + e0)) * math.log10(sigma_final / sigma_v0_psf)
            state = "Normally Consolidated (NC)"
        elif sigma_final <= sigma_p_psf:
            Sc_ft = (Cr * H0_ft / (1.0 + e0)) * math.log10(sigma_final / sigma_v0_psf)
            state = "Overconsolidated (OC - below sigma_p)"
        else:
            Sc_ft = (H0_ft / (1.0 + e0)) * (Cr * math.log10(sigma_p_psf / sigma_v0_psf) + Cc * math.log10(sigma_final / sigma_p_psf))
            state = "Overconsolidated (OC - piecewise crossing)"
        return {"settlement_inches": round(Sc_ft * 12.0, 2), "regime": state}

class MechanicalHydraulicsSolver:
    """Darcy-Weisbach Closed-Loop Piping & ASHRAE Erosion Velocity Check"""

    @staticmethod
    def calculate_pipe_head_loss(f: float, length_ft: float, diameter_in: float, velocity_fps: float) -> Dict[str, Any]:
        g = 32.174
        D_ft = diameter_in / 12.0
        hf = f * (length_ft / D_ft) * ((velocity_fps ** 2) / (2.0 * g))
        velocity_ok = 2.0 <= velocity_fps <= 10.0
        return {
            "head_loss_ft": round(hf, 2),
            "velocity_fps": velocity_fps,
            "ashrae_velocity_compliant": velocity_ok
        }

class SpatialClashVerifier:
    """AABB (Axis-Aligned Bounding Box) 3D Geometric Clash Audit"""

    @staticmethod
    def check_3d_clash(boxA: Tuple[float, float, float, float, float, float], 
                       boxB: Tuple[float, float, float, float, float, float]) -> bool:
        """box = (minX, minY, minZ, maxX, maxY, maxZ). Returns True if intersecting."""
        return (boxA[0] < boxB[3] and boxA[3] > boxB[0] and
                boxA[1] < boxB[4] and boxA[4] > boxB[1] and
                boxA[2] < boxB[5] and boxA[5] > boxB[2])
