[![Test Status](https://travis-ci.com/Cartmanishere/zippyshare-scraper.svg?branch=master)](https://travis-ci.com/Cartmanishere/zippyshare-scraper)

Check the [CHANGELOG](https://github.com/Cartmanishere/zippyshare-scraper/blob/master/CHANGELOG.md) for updates.

## Zippyshare Scraper:

This is a script to get direct download links to files from zippyshare. If you've used zippyshare to download anything then you know that you have to go to their page and click on the download now button to get the download started.

This script extracts the real download link from the page. You can directly feed that link to a downloader to get your download started.

This script is useful when working on remote servers where you don't have access to gui software.

### Reset Zippyshare Uploads:

If you're a zippyshare uploader, you know that zippyshare uploads are taken down if they're not downloaded in last 30 days.

You can use this script to reset the last download date without actually downloading the complete upload.

This script initiates the download of the file to test whether the link is working. Because of this, the last downloaded date for the file is also updated.

In this way, you can very easily extend the lifetime of your upload without wasting valuable time and bandwidth.


### Dependencies :

1. You need Python 3 environment to execute the script. You can easily install it from [here](https://www.python.org/downloads/).
2. Install the python dependencies:
```
	pip install requirements.txt
```

### Options:

| Arg | Value | Description |
| --- | --- | --- |
| `--in-file` | filepath | Path of the file containing zippyshare links to parse. |
| `--out-file` | filepath | Path of the file in which generated links will be stored. |
| `--dlc` | filepath | Path of a `.dlc` file. Takes precendence over `--in-file`. |
| `--filecrypt` | link | Link of a filecrypt container page. Note: It should not have a password or captcha. |
| `--engine` | `js`/`text`| Which engine to use for generating links. `js` by default. See `Engines` below for explanation. |

### Engines:

**History**

- This library used to work by scraping the zippyshare webpage.
- Parsing the javascript code to generate the link by regex matching.
- Whenever the source code of the site changed even slightly, this broke the regex matchers.
- Hence we ended up multiple different patterns that the site source code can have.

**Update**

- Instead of parsing the javascript using regex matching, the library has switched to executing the javascript code.
- The pure python implementation of javascript engine [js2py](https://github.com/PiotrDabkowski/Js2Py.git) is used for this.
- This should make the library more robust.

For now, I am keeping both the different approaches for getting the download links. These are the two engines -- 

- JsEngine
- TextEngine


### Usage :

1. Input links using an input file -- 
```python
python zippyshare.py --in-file input_links.txt --out-file links.txt
```

2. input links using dlc file -- 
```python
python zippyshare.py --dlc filename.dlc --out-file links.txt
```

3. Input links from terminal -- 
```python
python zippyshare.py
```


#### Examples :

Example of unprocessed link (this type of link will be input): ```http://www120.zippyshare.com/v/7DpZTYfi/file.html```

Example of Direct Downloadable link: ```http://www120.zippyshare.com/d/7DpZTYfi/4656/Ghost.In.The.Shell.S2.x265.7z.003```

#### (Optional) :

* You can then download from ```links.txt``` as follows:

```aria2c -i links.txt --file-allocation=none -c --auto-file-renaming=false```

```wget -nc -i links.txt```

* Or you can download using any other downloader you prefer.

### Known Issues :

* You have to run the script from the same network using which you are downloading files otherwise links may not work.

* The direct download links stop working after a few hours ( About 3-4 hrs, maybe). Don't know the exact time period.  At that point, you can rerun the script to get new download links to the same files which will work without problem.

* The script runs into an error when the "File not exist" zippyshare page loads.
### License :

This project is licensed under the terms of the MIT license.
