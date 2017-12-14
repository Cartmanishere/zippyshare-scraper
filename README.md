## Zippyshare Scraper :

This is a simple script to get direct download links to files from zippyshare. If you've used zippyshare to download anything then you know that you have to go to their page and click on the download now button to get the download started.

This script instead extracts the real download link from the page. You can directly feed that link to a downloader to get your download started.

This script is particularly useful when working on remote servers where you don't have access to gui software.

### Dependencies :

1. You need Python 3 environment to execute the script. You can easily install it from [here](https://www.python.org/downloads/).
2. You need the following packages installed.
```
	pip install requests
	pip install bs4
```

### Usage :

* You can run the script directly like -
```python zippyshare.py```
* You have 3 options to enter links.

1. Using file: You can put the zippyshare links in a file. Each link on a new line.

2. Using list: Enter link in the terminal one by one

3. Using dlc: Provide the path of the dlc file.

* After the links are processed, the result is displayed on terminal as well as the direct downloadable links are written to a ```links.txt``` file in the current working directory.

#### (Optional) :

* You can then download from ```links.txt``` as follows:

```aria2c -i links.txt --file-allocation=none -c --auto-file-renaming=false```

```wget -nc -i links.txt```

* Or you can download using any other downloader you prefer.

### Known Issues :

* You have to run the script on the same system which you are using for downloading otherwise some links may not work. ( Maybe Zippyshare uses IP logging to enable downloads ¯\\\_(ツ)_/¯ )

* The direct download links stop working after a few hours ( About 3-4 hrs, maybe). Don't know the exact time period.  At that point, you can rerun the script to get new download links to the same files which will work without problem.

### License :

This project is licensed under the terms of the MIT license.

