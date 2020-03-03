# FollowMe
 
This is the software for [MyPetBot](https://www.instructables.com/id/MyPetBot-A-Bot-That-Follows-You/), you can find the rest of the instructions on Instructables.

It is intended to track an object and follow it.

## Installation
Copy the folder FollowMe into your directory "Documents"


## Usage
The following command will launch the UI
```bash
  python3 Deployment/FollowMe.py
```

Then go to you ip address on port 8000 and you will find a button to Start the sequence and to Stop it.

### Sequence
* Takes a picture
* Sends it to the Intel Stick
* Analyse the content
* Save the Image
* Send command to the Arduino

The program does it with multithreading so that the only limiting factor is the inference time.
