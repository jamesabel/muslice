
**muslice**

Music Slicer program

Slices and remixes .wav files from a 4 channel TASCAM DR-40 portable recorder.

![Tascam DR-40](http://tascam.com/content/images/universal/product_detail/706/large/dr-40_ab_front.jpg)

The target application is where you set up the DR-40 to recorder to continually record a live performance.  
Here are the steps:

- Record an entire performance to the DR-40 in 4 channels (2 stereo channels).  You can just let it run and record.
- Download the .wav files to your Mac.
- Run `muslice` on those .wav files.  `muslice` will:
  - Convert the 2 stereo channels to 4 mono channels.
  - Calculate a 'VU meter' style time series of levels.
  - Normalize the channel volume levels for analysis.
  - Determine where the song breaks are and slice the input .wav files into segments (songs).
  - Create an initial stereo mix in both .wav and .mp3 formats.
