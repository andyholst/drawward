FROM ubuntu:20.04

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC

# Install dependencies for draw.io and Python
RUN apt-get update && apt-get install -y \
    wget xvfb libasound2 libgbm1 libgtk-3-0 libnss3 libx11-xcb1 libxtst6 libnotify4 libxss1 xdg-utils libsecret-1-0 dbus \
    python3.9 python3-pip && \
    wget https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/drawio-amd64-26.0.16.deb -O /tmp/drawio.deb && \
    dpkg -i /tmp/drawio.deb || apt-get install -f -y && \
    rm /tmp/drawio.deb && \
    pip3 install pyyaml==5.4.1 xmltodict==0.12.0 && \
    rm -rf /var/lib/apt/lists/*

# Copy scripts from the build context (now within drawward-cli/)
COPY convert_svg_to_xml.sh /usr/local/bin/
COPY convert_xml_to_backstage_files.py /usr/local/bin/
COPY entrypoint.sh /usr/local/bin/

# Ensure scripts are executable
RUN chmod +x /usr/local/bin/convert_svg_to_xml.sh /usr/local/bin/convert_xml_to_backstage_files.py /usr/local/bin/entrypoint.sh

# Set working directory
WORKDIR /app

# Define entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
