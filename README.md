music_organizer
===============
music_organizer is a small piece of software for organizing your music library, 
by re-formatting the album directory names and song file names.

Current features
----------------
* Directory and file name formatting
* Album cover art downloaing

Current supported audio file formats:
* Everything that's supported by the [tinytag](https://pypi.org/project/tinytag/) library:
    * MP3 (ID3 v1, v1.1, v2.2, v2.3+)
    * Wave
    * OGG
    * OPUS
    * FLAC
    * WMA
    * MP4/M4A 
   
Options
-------
The default formats for directory and file names are:
   `%A/%y - %a  # directory name, e.g. 'Metallica/1984 - Ride the Lightning'`
   `tn - %t     # file name, e.g. '01 - Fight Fire with Fire'`

Upcoming features
-----------------
* [muspy](https://muspy.com/) integration (Currently on-hold)
* [AcoustID](https://acoustid.org/) integration for identifying un-tagged audio files in library
    
3rd party resources
-------------------
* [pylast](https://pypi.org/project/pylast/)
* [mutagen](https://mutagen.readthedocs.io/en/latest/)
