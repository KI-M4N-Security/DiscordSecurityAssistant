FROM fedora:43

WORKDIR /app

# Install Python and minimal dependencies
RUN dnf update -y && \
    dnf install -y python3 python3-pip curl && \
    dnf clean all

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy integration services
COPY target_config_service.py ./
COPY integration_service.py ./

# Create non-root user
RUN groupadd -r -g 1001 integrationuser && \
    useradd -r -u 1001 -g integrationuser integrationuser && \
    chown -R integrationuser:integrationuser /app

USER integrationuser

# Default to integration service (can be overridden)
CMD ["python3", "integration_service.py"]