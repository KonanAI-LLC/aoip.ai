import librosa
from tqdm import tqdm
from typing import Dict, List

from .AbstractEvaluation import AbstractEvaluation
from concurrent.futures import ProcessPoolExecutor


class MultipleEvaluation(AbstractEvaluation):
    def __init__(self, sr: int, clean_paths: List[str], noisy_paths: List[str]):
        super().__init__(sr)
        if len(clean_paths) != len(noisy_paths):
            raise ValueError("clean_paths and noisy_paths must have the same length.")
        self.clean_audios = [librosa.load(path, sr=self.sr)[0] for path in tqdm(clean_paths)]
        self.noisy_audios = [librosa.load(path, sr=self.sr)[0] for path in tqdm(noisy_paths)]

    def _evaluate_single_pair(self, pair, func):
        clean_audio, noisy_audio = pair
        if func in [self.mosnet, self.srmr]:
            return func(noisy_audio)
        return func(clean_audio, noisy_audio)

    def evaluate_metric(self, metric_name: str) -> Dict[str, List[float]]:
        func = getattr(self, metric_name)
        initial_metric_results = self._evaluate_single_pair(
            (self.clean_audios[0], self.noisy_audios[0]), func
        )
        results = {key: [] for key in initial_metric_results.keys()}

        # Use a process pool executor to evaluate in parallel
        with ProcessPoolExecutor() as executor:
            for metric_result in executor.map(
                self._evaluate_single_pair,
                zip(self.clean_audios, self.noisy_audios),
                [func] * len(self.clean_audios),
            ):
                for key in metric_result.keys():
                    results[key].append(metric_result[key])

        return results


if __name__=="__main__":
    from pathlib import Path
    data = Path(__file__).parent.parent/"test_data"
    clean=str(data/"clean.wav")
    noisy=str(data/"noisy.wav")
    evaluator = MultipleEvaluation(
    16000, [clean,clean], [noisy,noisy]
)
    ALL_EVALUATION_METRICS = [
        'pesq',
        'stoi',
    ]
    for metric in ALL_EVALUATION_METRICS:
        results = evaluator.evaluate_metric(metric)
        print(results)
    # results = evaluator.evaluate_metric("composite")
    # print(results)  # Expected: {"stoi": [value1, value2]}

