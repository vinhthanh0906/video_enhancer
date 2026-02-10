# Setup 
- Caution: because mim was remove in 3.12 , so i suggest you use the 3.10 version of Python 

## Install Dependencies 
``` bash 
python -c "import torch; print(torch.__version__); print('cuda:', torch.cuda.is_available())"
pip install -U openmim
mim install "mmcv>=2.0.0"
mim install mmengine
mim install mmagic

````