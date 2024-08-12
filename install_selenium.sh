# Created with codemium
#!/bin/bash

# Install Chrome Browser
#sudo apt-get update
#sudo apt-get install -y wget unzip
#wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#sudo dpkg -i google-chrome-stable_current_amd64.deb
#sudo apt-get -f install

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")

wget https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
cd chromedriver-linux64
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
cd ..
rm chromedriver-linux64.zip

pip install selenium