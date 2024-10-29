import re, os, zipfile, requests, subprocess

class ChromeDriverDownloader:
    def __init__(self, version=None, directory_for_download=None, show_prints=True):
        self.version = version
        self.show_prints = show_prints
        self.directory_for_download = directory_for_download
        
        if self.directory_for_download is None:
            self.directory_for_download = os.getcwd()
        else:
            if not os.path.exists(self.directory_for_download):
                os.makedirs(self.directory_for_download)
        
        if self.version is None:
            if self.show_prints:
                print("Getting your current version from chrome...")
            self.version = self.__get_version()

    def __download_document(self, link, filename):
        try:
            response = requests.get(link, verify=True)
            with open(os.path.abspath(filename), 'wb') as file:
                file.write(response.content)
                
            if self.show_prints:
                print('File saved successfully.')
        except requests.exceptions.RequestException as e:
            if self.show_prints:
                print(f'Failed to download file {filename}: {e}')

    def __get_version(self):
        try:
            # for Windows
            result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],\
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            version = result.stdout.split()[-1]
            return re.findall(r'\d+\.\d+\.\d+', version)[0]
        except Exception as e:
            return f"Error: {e}"

    def __extract_chromedriver(self, zip_path):
        try:
            os.makedirs(self.directory_for_download, exist_ok=True)
            try:
                os.remove(os.path.abspath(f'{self.directory_for_download}/chromedriver.exe'))
            except FileNotFoundError:
                pass
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                chromedriver_path = next((item for item in zip_ref.namelist() if item.endswith('chromedriver.exe')), None)
                
                if chromedriver_path:
                    zip_ref.extract(chromedriver_path, self.directory_for_download)
                    
                    extracted_path = os.path.join(self.directory_for_download, chromedriver_path)
                    final_path = os.path.join(self.directory_for_download, 'chromedriver.exe')
                    os.rename(extracted_path, final_path)

                    for dirpath, dirnames, filenames in os.walk(self.directory_for_download, topdown=False):
                        if not os.listdir(dirpath):
                            os.rmdir(dirpath)

                    return True
                else:
                    print("O arquivo 'chromedriver.exe' não foi encontrado no zip.")
                    return False
        except zipfile.BadZipFile:
            print("O arquivo fornecido não é um arquivo zip válido.")
            return False
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            return False


    def download_chromedriver(self):
        url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
        response = requests.get(url)
        versions = list(response.json()['versions'])
        for version in versions:
            if self.version in version['version']:
                print(f"Your version is: {version['version']}")
                url_chromedriver = version['downloads']['chromedriver'][4]['url']
                self.__download_document(url_chromedriver, f'{self.directory_for_download}/chromedriver.zip')
                self.__extract_chromedriver(f'{self.directory_for_download}/chromedriver.zip')
                os.remove(f'{self.directory_for_download}/chromedriver.zip')
                break
            
        return os.path.abspath(f'{self.directory_for_download}/chromedriver.exe')
