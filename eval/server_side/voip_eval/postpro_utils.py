import numpy as np
import librosa
import scipy.signal
import scipy.io.wavfile
import matplotlib.pyplot as plt
import soundfile as sf
from tqdm import tqdm
from pathlib import Path
import glob
import re
import sys

get_file_count = lambda path: len(list(Path(path).rglob("*")))
global_sr = 16000


### Calculating Offset
def get_xcorr_max_lag(source, target, plot_flag=True, title=None):

    xcorr = scipy.signal.correlate(source, target)
    lags  = scipy.signal.correlation_lags(len(source), len(target))
    xcorr = xcorr / np.max(xcorr)
    t_max = lags[np.argmax(xcorr)]

    if plot_flag == True:
        plt.title(title)
        plt.plot(lags, xcorr)
        plt.show()

    return t_max


def aligned_breakdown(noisy, path_to_save, src_path, src_sequence, src_audio_len = 10, starting_lag_sec=1,gap_len=1):

    audio = src_audio_len*global_sr
    # 10 secs audio + 1 sec gap
    window = (src_audio_len+gap_len)*global_sr
    src_noisy = librosa.load(src_path/src_sequence[0], sr = global_sr)[0]
    print(noisy.shape)
    starting_window = int(starting_lag_sec*global_sr) # Some window to encorporate the starting lag
    print(starting_window)
    tmax = get_xcorr_max_lag(noisy[:starting_window], src_noisy, plot_flag=False ,title="Lag for Gmeet Cloud Auto")
    if tmax>0:
      noisy = noisy[tmax:]
    print(tmax, noisy.shape)

    for i in tqdm(range(len(src_sequence))):
      # if i in [120,121]:
        # continue
      print(noisy.shape)
      curr = noisy[:audio]

      print("Saved ",i, "th wav. Length ",len(curr)/global_sr, "sec.")
      assert len(curr) == audio
      print(str(path_to_save/src_sequence[i]))
      sf.write(path_to_save/src_sequence[i], curr, 16000, 'PCM_24')
      try:
          src_noisy = librosa.load(src_path/src_sequence[i+1], sr = global_sr)[0]

          noisy      = noisy[audio:]
          tmax = get_xcorr_max_lag(noisy[:window], src_noisy, plot_flag=False,title="Lag for Gmeet Cloud Auto")
          if tmax < 0 or abs(tmax - 5*global_sr) > 0.5*global_sr:
            print("---------------------------------------")
          noisy      = noisy[tmax:]
          print("Tmax: " + tmax, "     remaining wav: " + noisy.shape[0])
      except:
          continue


def split_raw(dataprefix,srcpattern,transmitted_file,split_dir_pattern,file_id,sr=16000, starting_lag_sec=1, seg_len=10,gap_len=1):
    get_ids = lambda p: int(re.split('_|\.', p.split("fileid_")[1])[0])
    my_list = sorted(glob.glob(str(dataprefix/(srcpattern.strip("/")+"/*"))), key=get_ids)
    my_list = [p.split("/")[-1] for p in my_list]
    src_path = dataprefix/srcpattern.strip("/")
    transmitted = librosa.load(transmitted_file, sr = sr)[0]
    OUTPUTDIR = dataprefix/split_dir_pattern.strip("/")/file_id
    OUTPUTDIR.mkdir(exist_ok=True,parents=True)
    aligned_breakdown(transmitted, OUTPUTDIR, src_path, my_list, src_audio_len=seg_len, gap_len=gap_len, starting_lag_sec=starting_lag_sec)
    assert get_file_count(OUTPUTDIR) == len(my_list)
    return "success\n"

if __name__=="__main__":
    assert len(sys.argv)>=5, "usage: python postpro.py datadir srcptrn raw_wav out_dir"
    dataprefix=Path(sys.argv[1]) # base dir for all data
    srcpattern=sys.argv[2] # relative path pattern from base dir to enclosing dir of gold wav files
    transmitted_file = Path(sys.argv[3]) # path to raw candidate wav file
    split_dir_pattern = sys.argv[4] # relative path from base dir to enclosing dir of dir containing splitted wavs
    file_id = transmitted_file.stem
    if len(sys.argv)==5:
        split_raw(dataprefix,srcpattern,transmitted_file,split_dir_pattern,file_id)
    else:
        seg_len=int(sys.argv[5])
        gap_len=int(sys.argv[6])
        split_raw(dataprefix,srcpattern,transmitted_file,split_dir_pattern,file_id,seg_len=seg_len,gap_len=gap_len)
