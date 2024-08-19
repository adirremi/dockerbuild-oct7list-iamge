# שלב 1: שימוש בתמונה בסיסית של Ubuntu שמותאמת ל-ARM64
FROM arm64v8/ubuntu:20.04

# הגדרת אזור זמן למניעת שאלה אינטראקטיבית
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Jerusalem

# עדכון מערכת והתקנת תלותים בסיסיים
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    python3 \
    python3-pip \
    python3-venv

# התקנת Chrome ו-ChromeDriver שמתאימים ל-ARM64
RUN wget -O /tmp/chrome-linux-arm64.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.119/linux-arm64/chrome-linux-arm64.zip \
    && unzip /tmp/chrome-linux-arm64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chrome-linux-arm64/chrome /usr/local/bin/google-chrome \
    && chmod +x /usr/local/bin/google-chrome \
    && rm /tmp/chrome-linux-arm64.zip

RUN wget -O /tmp/chromedriver-linux-arm64.zip https://storage.googleapis.com/chrome-for-testing-public/127.0.6533.119/linux-arm64/chromedriver-linux-arm64.zip \
    && unzip /tmp/chromedriver-linux-arm64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux-arm64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver-linux-arm64.zip

# יצירת סביבת וירטואליזציה והגדרת נתיב
RUN python3 -m venv /env
ENV PATH="/env/bin:$PATH"

# התקנת תלותים של Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת הקוד לתוך הקונטיינר
COPY . .

# הגדרת סביבת עבודה
WORKDIR /app

# הרצת הסקריפט
CMD ["python3", "main.py"]
