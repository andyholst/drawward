# Use a lightweight base image with bash and curl
FROM alpine:3.18

# Install bash and curl
RUN apk add --no-cache bash curl

# Download and install yq
RUN curl -sfL https://github.com/mikefarah/yq/releases/download/v4.35.1/yq_linux_amd64 -o /usr/local/bin/yq \
    && chmod +x /usr/local/bin/yq

# Verify yq installation
RUN yq --version

# Copy the compare_catalogs.sh script into the image
COPY compare_catalogs.sh /usr/local/bin/compare_catalogs.sh

# Make the script executable
RUN chmod +x /usr/local/bin/compare_catalogs.sh

# Set the entrypoint to the script
ENTRYPOINT ["/usr/local/bin/compare_catalogs.sh"]
