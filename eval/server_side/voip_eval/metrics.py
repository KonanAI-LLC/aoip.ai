
import numpy as np
import pystoi
import pysepm
import speechmetrics
from typing import Dict


_speechmetrics_mosnet = speechmetrics.load("mosnet", window=None)
_speechmetrics_srmr = speechmetrics.load("srmr", window=None)
_speechmetrics_pesq = speechmetrics.load("pesq", window=None)
_speechmetrics_sisdr = speechmetrics.load("sisdr", window=None)
_speechmetrics_bsseval = speechmetrics.load("bsseval", window=None)
_speechmetrics_stoi = speechmetrics.load("stoi", window=None)

def pystoi_stoi(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "stoi": pystoi.stoi(clean, noisy, sample_rate, extended=False),
    }


def pystoi_estoi(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "estoi": pystoi.stoi(clean, noisy, sample_rate, extended=True),
    }


def pysepm_cepstrum_distance(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "cepstrum_distance": pysepm.cepstrum_distance(clean, noisy, fs=sample_rate),
    }


def pysepm_composite(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    composite_result = pysepm.composite(clean, noisy, fs=sample_rate)
    return {
        "composite_1": composite_result[0],
        "composite_2": composite_result[1],
        "composite_3": composite_result[2],
    }


def pysepm_csii(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    csii_result = pysepm.csii(clean, noisy, sample_rate=sample_rate)
    return {
        "csii_1": csii_result[0],
        "csii_2": csii_result[1],
        "csii_3": csii_result[2],
    }


def pysepm_SNRseg(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "SNRseg": pysepm.SNRseg(clean, noisy, fs=sample_rate),
    }


def pysepm_fwSNRseg(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "fwSNRseg": pysepm.fwSNRseg(clean, noisy, fs=sample_rate),
    }


def pysepm_llr(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "llr": pysepm.llr(clean, noisy, fs=sample_rate),
    }


def pysepm_ncm(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "ncm": pysepm.ncm(clean, noisy, fs=sample_rate),
    }


def pysepm_pesq(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "pysepm_wb_pesq": pysepm.pesq(clean, noisy, fs=sample_rate)[1],
    }


def pysepm_stoi(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "pysepm_stoi": pysepm.stoi(clean, noisy, fs_sig=sample_rate),
    }


def speechmetrics_stoi(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "speechmatrics_stoi": _speechmetrics_stoi(noisy, clean, rate=sample_rate)[
            "stoi"
        ]
    }


def speechmetrics_pesq(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    pesq_scores = _speechmetrics_pesq(noisy, clean, rate=sample_rate)
    return {
        "nb_pesq": pesq_scores["nb_pesq"],
        "wb_pesq": pesq_scores["pesq"],
    }


def speechmetrics_bsseval(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    bsseval_scores = _speechmetrics_bsseval(noisy, clean, rate=sample_rate)
    return {
        "sdr": bsseval_scores["sdr"].item(),
        "isr": bsseval_scores["isr"].item(),
        "sar": bsseval_scores["sar"].item(),
    }


def speechmetrics_sisdr(
    clean: np.ndarray,
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    sisdr_scores = _speechmetrics_sisdr(noisy, clean, rate=sample_rate)
    return {
        "sisdr": sisdr_scores["sisdr"],
    }


def speechmetrics_mosnet(
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "mosnet": _speechmetrics_mosnet(noisy, rate=sample_rate)["mosnet"].item(),
    }


def speechmetrics_srmr(
    noisy: np.ndarray,
    sample_rate: int,
) -> Dict[str, float]:
    return {
        "srmr": _speechmetrics_srmr(noisy, rate=sample_rate)["srmr"],
    }


