FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy==2.4.3 \
    pandas==3.0.1 \
    matplotlib==3.10.8 \
    ipywidgets==8.1.8 \
    voila==0.5.11 \
    tabulate==0.10.0 \
    hatchling

# Copy and install the loan package
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir -e .

# Copy the notebook
COPY loan_amortization.ipynb .

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["voila", "loan_amortization.ipynb", \
     "--port=7860", \
     "--no-browser", \
     "--Voila.ip=0.0.0.0", \
     "--VoilaConfiguration.show_tracebacks=True"]
