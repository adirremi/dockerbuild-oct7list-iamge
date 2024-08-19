# שלב 1: שימוש בתמונה בסיסית של Ubuntu שמותאמת ל-x86/64
FROM ubuntu:20.04

# הגדרת אזור זמן למניעת שאלה אינטראקטיבית
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Jerusalem

# עדכון מערכת והתקנת תלותים בסיסיים ותלויות של Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libappindicator3-1 \
    libatspi2.0-0 \
    libpangoft2-1.0-0 \
    libxslt1.1 \
    libcurl4 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# התקנת Google Chrome Stable
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install \
    && rm google-chrome-stable_current_amd64.deb

# הורדת ChromeDriver וחילוצו למיקום הנכון
RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.119/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm /tmp/chromedriver-linux64.zip


# יצירת סביבת וירטואליזציה והגדרת נתיב
RUN python3 -m venv /env
ENV PATH="/env/bin:$PATH"
COPY . /app/
# התקנת תלותים של Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת הקוד לתוך הקונטיינר
COPY . .

# הגדרת סביבת עבודה
WORKDIR /app

# הרצת הסקריפט
CMD ["python3", "main.py"]
