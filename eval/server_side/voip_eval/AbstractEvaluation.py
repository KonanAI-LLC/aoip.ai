from abc import ABC
from typing import Dict
from voip_eval.metrics import (
    pystoi_stoi, pystoi_estoi, pysepm_cepstrum_distance, pysepm_composite,
    pysepm_csii, pysepm_SNRseg, pysepm_fwSNRseg, pysepm_llr, pysepm_ncm,
    pysepm_stoi, speechmetrics_pesq, speechmetrics_bsseval, speechmetrics_sisdr,
    speechmetrics_mosnet, speechmetrics_srmr)


import numpy as np

class AbstractEvaluation(ABC):
    def __init__(self, sr: int):
        self.sr = sr

    def stoi(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pystoi_stoi(clean, noisy, self.sr)

    def estoi(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pystoi_estoi(clean, noisy, self.sr)

    def cepstrum_distance(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_cepstrum_distance(clean, noisy, self.sr)

    def composite(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_composite(clean, noisy, self.sr)

    def csii(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_csii(clean, noisy, self.sr)

    def SNRseg(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_SNRseg(clean, noisy, self.sr)

    def fwSNRseg(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_fwSNRseg(clean, noisy, self.sr)

    def llr(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_llr(clean, noisy, self.sr)

    def ncm(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_ncm(clean, noisy, self.sr)

    def wss(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return pysepm_stoi(clean, noisy, self.sr)

    def pesq(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return speechmetrics_pesq(clean, noisy, self.sr)

    def bsseval(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return speechmetrics_bsseval(clean, noisy, self.sr)

    def sisdr(
        self,
        clean: np.ndarray,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return speechmetrics_sisdr(clean, noisy, self.sr)

    def mosnet(
        self,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return speechmetrics_mosnet(noisy, self.sr)

    def srmr(
        self,
        noisy: np.ndarray,
    ) -> Dict[str, float]:
        return speechmetrics_srmr(noisy, self.sr)

    def evaluate_all_pairs_for_metric(self, func):
        results = []
        clean_audios = self.clean_audios
        noisy_audios = self.noisy_audios

        for clean_audio, noisy_audio in zip(clean_audios, noisy_audios):
            if func in [self.mosnet, self.srmr]:
                results.append(func(noisy_audio))
            else:
                results.append(func(clean_audio, noisy_audio))
        return results

    def all_metrics(self):
        results = {}

        functions_relative = [
            self.stoi,
            self.estoi,
            self.cepstrum_distance,
            self.composite,
            self.csii,
            self.SNRseg,
            self.fwSNRseg,
            self.llr,
            self.ncm,
            self.wss,
            self.pesq,
            self.bsseval,
            self.sisdr,
        ]

        functions_absolute = [self.mosnet, self.srmr]

        for func in functions_relative + functions_absolute:
            func_results = self.evaluate_all_pairs_for_metric(func)[0]
            results.update(func_results)

        return results

