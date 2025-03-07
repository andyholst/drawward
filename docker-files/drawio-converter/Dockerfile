FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN echo "Installing dependencies..." \
    && apt-get update \
    && apt-get install -y \
        wget \
        xvfb \
        libasound2 \
        libgbm1 \
        libgtk-3-0 \
        libnss3 \
        libx11-xcb1 \
        libxtst6 \
        libnotify4 \
        libxss1 \
        xdg-utils \
        libsecret-1-0 \
        dbus \
    && echo "Dependencies installed successfully" \
    && rm -rf /var/lib/apt/lists/*

RUN echo "Downloading draw.io .deb package..." \
    && wget https://github.com/jgraph/drawio-desktop/releases/download/v26.0.16/drawio-amd64-26.0.16.deb -O /tmp/drawio.deb \
    && echo "Installing draw.io.deb package..." \
    && dpkg -i /tmp/drawio.deb || apt-get install -f -y \
    && echo "Listing installed files from the .deb package (may fail if not registered):" \
    && dpkg -L drawio || true \
    && echo "Checking drawio binary location:" \
    && ls -l /usr/bin/drawio \
    && echo "draw.io installation completed" \
    && rm /tmp/drawio.deb

COPY convert_svg_to_xml.sh /usr/local/bin/convert_svg_to_xml.sh
RUN echo "Setting up convert_svg_to_xml.sh..." \
    && chmod +x /usr/local/bin/convert_svg_to_xml.sh \
    && echo "convert_svg_to_xml.sh ready at /usr/local/bin/convert_svg_to_xml.sh"

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/convert_svg_to_xml.sh"]
