mkdir ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
# source ~/.bashrc
export PATH="~/miniconda3/bin:$PATH"
conda create -n voip-eval python=3.10 -y
conda activate voip-eval
conda install -c conda-forge ffmpeg -y
pip install flask
pip install numpy==1.23.5
pip install stempeg                                                                                           
pip install git+https://github.com/aliutkus/speechmetrics#egg=speechmetrics
pip3 install https://github.com/schmiph2/pysepm/archive/master.zip
pip install librosa
pip install matplotlib
pip install tqdm
