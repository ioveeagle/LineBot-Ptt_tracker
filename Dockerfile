FROM python3.6
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .