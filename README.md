#### Updates:

##### 18 Feb 2020
- Added a fifth pattern. Update the scripts. 
 
##### 5 Feb 2020
- Added a fourth pattern based on changed zippyshare logic. Update your scripts.

##### 25 Oct 2019
- Refactored the different variations of the zippyshare page into a single script.
- Added multi-threading to speed up link extraction. 
- Check the new usage method since that is also changed.

## Zippyshare Scraper:

This is a script to get direct download links to files from zippyshare. If you've used zippyshare to download anything then you know that you have to go to their page and click on the download now button to get the download started.

This script extracts the real download link from the page. You can directly feed that link to a downloader to get your download started.

This script is useful when working on remote servers where you don't have access to gui software.

### Reset Zippyshare Uploads:

If you're a zippyshare uploader, you know that zippyshare uploads are taken down if they're not downloaded in last 30 days.

You can use this script to reset the last download date without actually downloading the complete upload.

This script initiates the download of the file to test whether the link is working. Because of this, the last downloaded date for the file is also updated.

In this way, you can very easily extend the lifetime of your upload without wasting valuable time and bandwidth.

### NOTICE :

Zippyshare sometimes updates their source code on the webpage which breaks the link extraction. This script already takes care of 3 variations of the zippyshare webpage.
In case the script stops working due to one of their updates, please raise an issue and I will fix it asap.
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

You have 3 options to enter links.

* Using file: You can put the zippyshare links in a file. Each link on a new line.
```
python zippyshare.py --in-file <path_to_file_containing_links>
```
* Using dlc: Provide the path of the dlc file.
```
python zippyshare.py --dlc-file <path_to_dlc_file>
```
* Using list: Enter link in the terminal one by one

* After the links are processed, the result is displayed on terminal as well as the direct downloadable links are written to a ```links.txt``` file in the current working directory. 
You can change the default output file as follows:
```
python zippyshare.py --out-file <output_file_path>
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

