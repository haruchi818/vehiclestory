FROM ubuntu:23.04

# Python <3
USER root
WORKDIR /root
RUN apt -y update
RUN apt -y upgrade
RUN apt-get -y install wget python3.11 python3.11-venv python3-pip
RUN apt install -y unzip
RUN apt install -y tr ca-certificates fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 wget xdg-utils xvfb

# ADD tools/Linux_x64_1141586_chrome-linux.zip /root/Linux_x64_1141586_chrome-linux.zip
# ADD tools/Linux_x64_1141586_chromedriver_linux64.zip /root/Linux_x64_1141586_chromedriver_linux64.zip
RUN wget "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1141586%2Fchrome-linux.zip?generation=1683664847939114&alt=media" -O chrome-linux.zip
RUN wget "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1141586%2Fchromedriver_linux64.zip?generation=1683664852754048&alt=media" -O chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN cd / && unzip /root/chrome-linux.zip
RUN mv chromedriver_linux64/chromedriver /usr/local/bin

ARG USER_ID
ENV USER_ID=$USER_ID
RUN useradd -l -m -d /home/tester -u $USER_ID -g root -s /bin/bash tester
RUN chmod 777 -R /home/tester
RUN chown tester -R /home/tester

USER tester
WORKDIR /home/tester
RUN python3.11 -m venv env
RUN /home/tester/env/bin/pip install selenium pandas beautifulsoup4 flask
RUN . env/bin/activate
ENV DISPLAY :99
ADD vehicle_story.py /home/tester/
CMD ["/bin/sh", "-c", "/usr/bin/nohup /usr/bin/Xvfb :99 -screen 0 1920x1080x16 -nolisten tcp | /home/tester/env/bin/python vehicle_story.py"]