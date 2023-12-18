
import argparse
from pathlib import Path
import glob
import pandas as pd

def extract_id_from_filename(filename):
    filename = Path(filename).stem
    filename = filename.replace("eval_results_clean_","")
    return filename

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataprefix", type=Path, default=Path.home()/"data/results",
    help="Path to enclosing folder with original splitted source audio")
    parser.add_argument("--eval_pattern", type=str, default="clean",
    help="Name of the evaluation run to save json output")
    args = parser.parse_args()
    
    DATAPREFIX=args.dataprefix
    output_csv_pattern = str(DATAPREFIX/f"eval_results_{args.eval_pattern}_*.csv")   
    output_csv_paths = glob.glob(output_csv_pattern)
    result=[]
    for path in output_csv_paths:
        # import pdb;pdb.set_trace()
        # bw = '_'.join(path.replace("_kbps","").split("_")[-2:]).replace("clean_","")\
        #    .replace("record_","").split(".")[0]
        # print("#"*15,"bandwidth:",bw,"#"*15)
        df = pd.read_csv(path)
        file_id = extract_id_from_filename(path) 
        mean = df.select_dtypes(include=['number']).mean()
        # mean['Bandwidth'] = int(bw)
        # mean.name=bw
        std = df.select_dtypes(include=['number']).std()
        # std.name=bw

        formatted_series = pd.Series([f"{m:.2f} ± {s:.2f}" for m, s in zip(mean, std)], index=mean.index)
        formatted_series.name=file_id
        result.append(formatted_series)
        # print(df.select_dtypes(include=['number']).mean())
        # print(df.select_dtypes(include=['number']).std())
        # print("-"*30)
    df = pd.concat(result, axis=1).T
    df.to_csv(f"all_test_results_{args.eval_pattern}.csv")
# print(df)
# print(df.sort_values(by=['Bandwidth']))
# print(df.sort_index(key=lambda x: int(x.split("_")[0])))
# extracted = df.index.str.extract('(\d+)').astype(int)
# extracted.index=df.index
# df['sort_key']=extracted

# Sort the DataFrame based on the extracted integer values
# df = df.sort_values('sort_key').drop('sort_key', axis=1)
    print(df.head())
    print(len(df))
