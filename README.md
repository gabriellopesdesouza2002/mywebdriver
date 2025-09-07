# mywebdriver - A quick library to install your webdriver according to your browser version

## Instalation

`pip install -U mywebdriver`

## Use

```python
from mywebdriver.chrome.chromedriver import ChromeDriverDownloader

PATH_CHOMEDRIVER = ChromeDriverDownloader(directory_for_download='bin').download_chromedriver()
```
