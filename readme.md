
## muslice ##

Music Slicer program by [James Abel](www.abel.co).

Slices and remixes .wav files from a 4 channel TASCAM DR-40 portable recorder.

![Tascam DR-40](http://tascam.com/content/images/universal/misc/dr-40_front.jpg)

The target application is where you set up the DR-40 to recorder to continually record a live performance and 
you'd like an automated program to slice the .wav files up into individual songs as well as create an initial 
stereo mix as standard .mp3 files.  You can them listen to these .mp3 mixes to see which songs you want to go 
back to and manually remix, enhance and master.
  
Here are the steps:

- Record an entire performance to the DR-40 in 4 channels (2 stereo channels).  You can just let it run and record.  A
  typical use is to start/stop recording at the start/end of each set.
- Download the .wav files to your Mac.
- Run `muslice` on those .wav files.  `muslice` will:
  - Convert the 2 stereo channels to 4 mono channels.
  - Calculate a 'VU meter' style time series of levels in the form of .png image files and .json text files.
  - Normalize the channel volume levels for analysis, which is useful if the individual channels were recorded 
    at different levels.
  - Determine where the song breaks are and slice the input .wav files into segments (songs).  These .wav file can 
    also be imported into your DAW (e.g. ProTools) for manual remixing, enhancement and mastering.
  - Create an initial stereo mix in both .wav and .mp3 formats.


## Requirements ##

Requirements (must be installed on your Mac):

- [Python 3](https://www.python.org/) interpreter.
- [SoX](http://sox.sourceforge.net/), the Swiss Army knife of sound processing programs.

On MacX/OSX these are installable using [homebrew](https://brew.sh/).
