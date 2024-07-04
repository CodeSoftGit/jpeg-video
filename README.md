# jpeg-video
Apply JPEG compression to your videos.

Example video:

[![Example Video | YouTube](https://img.youtube.com/vi/DjFKzz1Rbak/0.jpg)](https://www.youtube.com/watch?v=DjFKzz1Rbak)

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/CodeSoftGit/jpeg-video">jpeg-video</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://github.com/CodeSoftGit">CodeSoftGit</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Creative Commons Attribution 4.0 International<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""></a></p>

## Dependencies
- PyQt5  (Pip)
- ffmpeg (Package manager of choice, must be added to path or in same directory)

## Additional Notes
When progress bar reads "Extracting frames - 0%" it is still processing. FFmpeg does not provide a progress indicator for us to leverage.