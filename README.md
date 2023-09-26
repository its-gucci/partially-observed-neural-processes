# [Generalizable Neural Fields as Partially Observed Neural Processes](https://its-gucci.github.io/ponp/)

Code for reproducing the experiments in the [paper](https://arxiv.org/pdf/2309.06660.pdf):
```
@article{gu2023generalizable,
  title={Generalizable Neural Fields as Partially Observed Neural Processes},
  author={Gu, Jeffrey and Wang, Kuan-Chieh and Yeung, Serena},
  journal={arXiv preprint arXiv:2309.06660},
  year={2023}
}
```

## Prerequisites

`pip install -r requirements.txt`

## Data

Create a directory named `data` and download the CT scan data from [this link](https://drive.google.com/drive/folders/1SVHKRQXiRb98q4KHVEbj8eoWxjNS2QLW) and put it into the `data` folder.   

## Experiments

In `2D_CT_Recon.ipynb`, we provide an example of how our AttnLNP model for 2D CT Reconstruction was trained and evaluated. A sample trained model is provided in the `saved_models` directory. 

## Acknowledgements

Our implementation leverages the [Neural Process Family repository](https://github.com/YannDubs/Neural-Process-Family):
```
@misc{dubois2020npf,
  title        = {Neural Process Family},
  author       = {Dubois, Yann and Gordon, Jonathan and Foong, Andrew YK},
  month        = {September},
  year         = {2020},
  howpublished = {\url{http://yanndubs.github.io/Neural-Process-Family/}}
}
```
The 2D CT scan data is courtesy of [LearnIt](https://www.matthewtancik.com/learnit):
```
@inproceedings{tancik2021learned,
  title={Learned initializations for optimizing coordinate-based neural representations},
  author={Tancik, Matthew and Mildenhall, Ben and Wang, Terrance and Schmidt, Divi and Srinivasan, Pratul P and Barron, Jonathan T and Ng, Ren},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={2846--2855},
  year={2021}
}
```
