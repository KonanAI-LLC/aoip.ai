conda create -n enh python=3.8 -y
conda activate enh
git clone https://github.com/YunyangZeng/TAPLoss.git
pip install julius hydra_core==0.11.3 hydra_colorlog==0.1.4 pystoi==0.3.3 git+https://github.com/ludlows/python-pesq#egg=pesq 
pip install six==1.16.0 sounddevice torchaudio==0.13.1 torch==1.13.1
mkdir data
mkdir data/src_test
wget https://cmu.box.com/shared/static/cds26b2grgekszptc17a1ckljuocqyzq --content-disposition --show-progress
unzip src_noisy.zip -d data/src_test/
rm src_noisy.zip
