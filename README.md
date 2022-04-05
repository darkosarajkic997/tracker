# OPEN CV Python tracker 
Track center of any area on input video/cam and create croped video of tracked area

## Requirements
Install requirements from requirements.txt file
  * pip install -r requirements.txt

## Usage
Run tracker script
python tracker.py 
with optional arguments:
  * **--video**: path to video, if none is provided script will try to find build-in camera
  * **--tracker**: tracker type, find optinos on OpenCV official web site
  * **--dir_name**: name of directory where output video and crops will be saved
