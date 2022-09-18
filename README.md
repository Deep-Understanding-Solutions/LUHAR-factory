<p align="center">
  <img src="https://gcdnb.pbrd.co/images/vU7OIQGrTN7W.png" align="center" width="200" style="border-radius: 20px;"/>
</p>

# LUHAR-factory
This project includes the LUHAR dataset - large CSV file containing thousands of articles written in Slovak language, labeled as realiable or unreliable. It also includes scripts used to scrap the articles from public resources.

# Scrapping scrips
Scrapping scrips are written in python. The structure of this project is designed to isolate each resource (media) to it's own space. The rule goes as follows:

`/src/{media-name}` - Identifies given resource folder,

`/src/{media-name}/data.csv` - identifies given resource dataset, the fragment of LUHAR,

`/src/{media-name}/parse.py` - identifies the scrapping script. It has persistent behavior and can resume it's work even if interrupted.

More scripts included are:

`/src/desribe.py` - Outputs information about dataset to terminal,

`/src/defragment.py` - build LUHAR.csv by combining all fragments.
