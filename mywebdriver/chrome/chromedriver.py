import re, os, zipfile, requests, subprocess, platform, shutil

class ChromeDriverDownloader:
    def __init__(self, version=None, directory_for_download=None, show_prints=True, allways_download=False):
        self.URL = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
        self.version = version
        self.show_prints = show_prints
        self.directory_for_download = directory_for_download
        self.allways_download = allways_download
        
        
        if self.directory_for_download is None:
            self.directory_for_download = os.getcwd()
        else:
            if not os.path.exists(self.directory_for_download):
                os.makedirs(self.directory_for_download)
        
        if self.version is None:
            if self.show_prints:
                print("Getting your current version from chrome...")
            self.version = self.__get_version()

    def __download_file(self, link, filename):
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
        if self.allways_download == False:
            if os.path.exists(os.path.abspath(f'{self.directory_for_download}/chromedriver.exe')):
                print("Chromedriver already downloaded")
                return os.path.abspath(f'{self.directory_for_download}/chromedriver.exe')
            else:
                pass
        else:
            pass
        response = requests.get(self.URL)
        versions = list(response.json()['versions'])
        for version in versions:
            if self.version in version['version']:
                print(f"Your version is: {version['version']}")
                url_chromedriver = version['downloads']['chromedriver'][4]['url']
                self.__download_file(url_chromedriver, f'{self.directory_for_download}/chromedriver.zip')
                self.__extract_chromedriver(f'{self.directory_for_download}/chromedriver.zip')
                os.remove(f'{self.directory_for_download}/chromedriver.zip')
                break
            
        return os.path.abspath(f'{self.directory_for_download}/chromedriver.exe')

class ChromeDriverDownloaderLinux:
    def __init__(self, version=None, directory_for_download='bin', show_prints=True, allways_download=False):
        self.URL = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
        self.directory_for_download = directory_for_download
        self.show_prints = show_prints
        self.allways_download = allways_download
        if not os.path.exists(self.directory_for_download):
            os.makedirs(self.directory_for_download)

        if version is None:
            if self.show_prints:
                print("Detectando a versão do Chrome instalada...")
            version = self.__get_chrome_version()
            if self.show_prints:
                print(f"Versão detectada: {version}")
        self.version = version

    def __get_chrome_version(self):
        try:
            for chrome_bin in ['google-chrome', 'chrome', 'chromium', 'chromium-browser']:
                try:
                    output = subprocess.check_output([chrome_bin, '--version'], text=True)
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
                    if match:
                        return match.group(1)
                except Exception:
                    continue
            raise RuntimeError("Chrome/Chromium não encontrado no PATH!")
        except Exception as e:
            raise RuntimeError(f"Erro ao detectar versão do Chrome: {e}")

    def download_chromedriver(self):
        chromedriver_path = os.path.abspath(os.path.join(self.directory_for_download, 'chromedriver'))
        if not self.allways_download and os.path.exists(chromedriver_path):
            if self.show_prints:
                print("Chromedriver já existe.")
            if self._validate_chromedriver(chromedriver_path):
                return chromedriver_path
            else:
                if self.show_prints:
                    print("Chromedriver existente inválido, removendo...")
                os.remove(chromedriver_path)

        response = requests.get(self.URL)
        data = response.json()['versions']

        chosen = None
        for entry in data:
            if self.version in entry['version']:
                chosen = entry
                break
        if not chosen:
            raise RuntimeError("Versão do Chrome não encontrada na lista de chromedriver.")

        arch = platform.machine()
        if arch == 'x86_64':
            platform_key = 'linux64'
            file_suffix = 'chromedriver-linux64.zip'
        elif arch in ['aarch64', 'arm64']:
            platform_key = 'linux-arm64'
            file_suffix = 'chromedriver-linux-arm64.zip'
        elif arch == 'armv7l':
            platform_key = 'linux-armv7l'
            file_suffix = 'chromedriver-linux-armv7l.zip'
        else:
            raise RuntimeError(f'Arquitetura não suportada: {arch}')

        url_chromedriver = None
        for d in chosen['downloads']['chromedriver']:
            if d['platform'] == platform_key and d['url'].endswith(file_suffix):
                url_chromedriver = d['url']
                break

        if not url_chromedriver:
            raise RuntimeError(f"Download para {platform_key} não encontrado.")

        zip_path = os.path.join(self.directory_for_download, 'chromedriver.zip')
        self.__download_file(url_chromedriver, zip_path)
        self.__extract_chromedriver(zip_path, chromedriver_path)
        os.remove(zip_path)
        if not self._validate_chromedriver(chromedriver_path):
            raise RuntimeError("O chromedriver baixado não é um binário válido para x86_64!")
        return chromedriver_path

    def __download_file(self, link, filename):
        r = requests.get(link, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        if self.show_prints:
            print(f'Arquivo salvo em: {filename}')

    def __extract_chromedriver(self, zip_path, chromedriver_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Pega apenas o arquivo chamado "chromedriver" (ignora LICENSE)
            chromedriver_file = next(
                (name for name in zip_ref.namelist()
                 if name.split('/')[-1] == 'chromedriver'),
                None
            )
            if not chromedriver_file:
                raise RuntimeError("Arquivo 'chromedriver' não encontrado no zip.")
            # Extrai para pasta temporária
            extract_dir = os.path.join(self.directory_for_download, 'tmp_extract')
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            zip_ref.extract(chromedriver_file, extract_dir)
            src = os.path.join(extract_dir, chromedriver_file)
            shutil.move(src, chromedriver_path)
            shutil.rmtree(extract_dir)
            os.chmod(chromedriver_path, 0o755)
            if self.show_prints:
                print(f"Chromedriver extraído em: {chromedriver_path}")

    def _validate_chromedriver(self, chromedriver_path):
        try:
            out = subprocess.check_output(['file', chromedriver_path], text=True)
            return ('ELF 64-bit' in out) and ('x86-64' in out)
        except Exception:
            return False
