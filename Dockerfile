FROM python:3.11-slim

# Không tạo .pyc và log ra terminal ngay
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài package hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-jdk \
    libpq-dev \
    curl \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước để tận dụng cache build
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Mặc định giữ container sống để có thể exec vào nếu cần
CMD ["tail", "-f", "/dev/null"]