FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    numpy>=1.24.0 \
    pandas>=2.0.0 \
    matplotlib>=3.7.0 \
    ipywidgets>=8.0.0 \
    voila>=0.5.0 \
    hatchling>=1.18.0

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

