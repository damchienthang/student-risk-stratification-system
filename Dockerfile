# Đóng gói ứng dụng để triển khai mọi nơi
FROM python:3.11-slim

# Thư mục làm việc
WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source
COPY . .

# Expose port
EXPOSE 8000

# Biến môi trường mặc định
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

# Chạy server
CMD ["python", "main.py"]
