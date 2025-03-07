FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml xmltodict

COPY convert_xml_to_backstage_files.py /usr/local/bin/convert_xml_to_backstage_files.py
RUN chmod +x /usr/local/bin/convert_xml_to_backstage_files.py

ENTRYPOINT ["/usr/local/bin/convert_xml_to_backstage_files.py"]
