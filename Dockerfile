FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (templates, static assets, code modules)
COPY . .

# Set dynamic port default (Hugging Face Spaces uses 7860, Render uses 10000 or custom)
ENV PORT=5000

# Launch server with Gunicorn, evaluating the port variable at startup
CMD gunicorn -b 0.0.0.0:$PORT app:app
