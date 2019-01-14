# XCoder
Compress / Decompress Brawl Stars SC files on Windows / Linux / Android!

### Credits
This tool is based on:
- <a href="https://github.com/Xset-s/png2sc">png2sc</a>, Developer: <a href="https://github.com/Xset-s">Xset-s</a>
- <a href="https://github.com/Galaxy1036/scPacker">scPacker</a>, Developer: <a href="https://github.com/Galaxy1036">Galaxy1036</a></br>

I wanna say "Thank You!" to these developers, because without their work XCoder wouldn't have been released!</br>

### Features:
- Easy to use.
- Brawl Stars support.
- Multiplatform support (working on Windows, Linux and Android).
- SC compilation / decompilation.

### How to install
On Windows:
- Download Python 3.5 or newer version from <a href="https://www.python.org/downloads/">official page</a>.
- Install Python. While Installing, enable such parameters as "Add Python to PATH", "Install pip", "Install py launcher", "Associate files with Python" and "Add Python to environment variables".
- Download XCoder from <a href="https://github.com/MasterDevX/XCoder/releases">releases page</a> and extract it.
- Execute "Init.py" file to install required modules and create workspace directories.</br>

On Linux:
- Open Terminal and install Python by executing following command:</br>
```sudo apt-get update && sudo apt-get install python3 python3-pip```
- Download XCoder from <a href="https://github.com/MasterDevX/XCoder/releases">releases page</a> and extract it.
- Execute "Init.py" file to install required modules and create workspace directories.</br>

On Android:
- Download and install PyDroid app from <a href="https://play.google.com/store/apps/details?id=ru.iiec.pydroid3">Google Play</a>.
- Open PyDroid and wait until Python installs.
- Download XCoder from <a href="https://github.com/MasterDevX/XCoder/releases">releases page</a> and extract it.
- In PyDroid open and execute "Init.py" file to install required modules and create workspace directories.</br>

### How to use
- To compile SC:</br>
Put folders with texture name and .png files inside them in the "In-Decompressed-SC" directory and execute "SC-Encode.py" script. After the process will be finished, your .sc files will appear in "Out-Compressed-SC" folder.
- To decompile SC:</br>
Put .sc files in the "In-Compressed-SC" directory and execute "SC-Decode.py" script. After the process will be finished, your .png files will appear in "Out-Decompressed-SC" folder.</br>

### TODO:
- Clash of Clans support.
- Clash Royale support.
- CSV compilation / decompilation.
