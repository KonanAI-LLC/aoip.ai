import librosa
from voip_eval.AbstractEvaluation import AbstractEvaluation


class SingleEvaluation(AbstractEvaluation):
    """
    Evaluate metrics on a single pair of clean and noisy audio.
    """
    def __init__(self, sr, clean_path, noisy_path):
        super().__init__(sr)
        self.clean_audios = [librosa.load(clean_path, sr=self.sr)[0]]
        self.noisy_audios = [librosa.load(noisy_path, sr=self.sr)[0]]

    def evaluate_metric(self, metric_name):
        func = getattr(self, metric_name)
        if metric_name == "all_metrics":
            return func()
        if func in [self.mosnet, self.srmr]:
            return func(self.noisy_audios[0])
        return func(self.clean_audios[0], self.noisy_audios[0])

if __name__=="__main__":
    # Using the metric name as a string:
    from pathlib import Path
    data = Path.home()/"voip-eval/test_data"
    single_eval = SingleEvaluation(16000, str(data/"clean.wav"), str(data/"noisy.wav"))
    ALL_EVALUATION_METRICS = [
        'pesq',
        'stoi',
    ]
    for metric in ALL_EVALUATION_METRICS:
        #results = evaluator.evaluate_metric(metric)
        #print(results)
        print(single_eval.evaluate_metric(metric))
