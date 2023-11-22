from typing import List
from pathlib import Path
import argparse
import glob
import sys
import pandas as pd
from tqdm import tqdm
import re
sys.path.append(str(Path(__file__).parent.parent))
from voip_eval.MultipleEvaluation import MultipleEvaluation


def evaluate_metrics_to_csv(clean_paths: List[str], noisy_paths: List[str], metrics: List[str], output_csv_path: str):
    evaluator = MultipleEvaluation(sr=16000, clean_paths=clean_paths, noisy_paths=noisy_paths)
    final_results = {}

    # tqdm loop over metrics
    for metric in tqdm(metrics, desc="Metrics", leave=False):
        metric_results = evaluator.evaluate_metric(metric)

        # tqdm loop over the number of paths
        for clean_path, noisy_path in tqdm(zip(clean_paths, noisy_paths), total=len(clean_paths), desc=f"Evaluating {metric}", leave=False):
            # Concatenate clean and noisy paths to form a unique key for the results dictionary
            path_key = f"{clean_path}__{noisy_path}"

            if path_key not in final_results:
                final_results[path_key] = {}

            for key, values in metric_results.items():
                # Assuming the order of values corresponds to the order of paths
                final_results[path_key][key] = values[clean_paths.index(clean_path)]

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(final_results).T
    df = df.astype('float32')
    df.to_csv(output_csv_path)


def evaluate_(dataprefix,split_pattern,src_pattern,eval_pattern,file_id):
    """
    run and return evaluate metrics
    args:
    dataprefix: path to data folder (for all data, raw or processed)
    split_pattern: path to the parent dir of all splitted relayed audio dirs relative to dataprefix
    src_pattern: path to the clean ground truth audio dirs relative to dataprefix (always use clean-radix!!!)
    eval_pattern: basically the version (clean/noisy) of the run, part of the output csv name
    file_id: name of the splitted audio dir under srcpattern, basically the run_id
    """
    ALL_EVALUATION_METRICS = [
        'pesq',
        'stoi',
    ]
    DATAPREFIX=dataprefix
    TARGET_DIR = DATAPREFIX/src_pattern

    splitted_dir = DATAPREFIX/split_pattern/file_id

    get_ids = lambda p: int(re.split('_|\.', p.split("fileid_")[1])[0])

    print(splitted_dir, file_id)
    splitted_files_regex = str(splitted_dir) + "/*"
        
    relayed_paths = sorted(glob.glob(str(splitted_files_regex)), key=get_ids)
    original_paths = sorted(glob.glob(str(TARGET_DIR/"*")), key=get_ids)
    print(len(original_paths), len(relayed_paths))
    assert (len(original_paths)==len(relayed_paths))
      

    EVAL_DIR = DATAPREFIX/"results"
    EVAL_DIR.mkdir(exist_ok=True,parents=True)
    output_csv_path = str(EVAL_DIR/f"eval_results_{eval_pattern}_{file_id}.csv")   
    evaluate_metrics_to_csv(original_paths, relayed_paths, ALL_EVALUATION_METRICS, output_csv_path)
    df = pd.read_csv(output_csv_path)
    mean = df.select_dtypes(include=['number']).mean()
    std = df.select_dtypes(include=['number']).std()
    formatted_series = pd.Series([f"{m:.3f}+-{s:.3f}" for m, s in zip(mean, std)], index=mean.index)
    formatted_series.name=file_id
    return formatted_series.to_dict()


if __name__=="__main__":
    assert len(sys.argv)==6, "usage: python eval_util.py datadir splitptrn src_ptrn eval_ptrn(clean/noisy) fileid"
    dataprefix=Path(sys.argv[1]) # base dir for all data 
    split_dir_pattern = sys.argv[2] # relative path from base dir to enclosing dir of dir containing splitted wavs
    srcpattern=sys.argv[3] # relative path pattern from base dir to enclosing dir of gold wav files
    assert "clean" in srcpattern
    eval_ptrn=sys.argv[4]
    file_id = sys.argv[5]
    res = evaluate_(dataprefix,split_dir_pattern,srcpattern,eval_ptrn,file_id)
    print(res)
