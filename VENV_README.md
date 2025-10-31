# Shared Virtual Environment Setup

This project uses a shared virtual environment located in the root directory.

## Activation

To activate the shared virtual environment:

### Windows (PowerShell)
```powershell
.\venv\Scripts\activate.ps1
```

### Linux/Mac
```bash
source venv/bin/activate
```

## Usage

Once activated, you can run any Python scripts from any component:

```bash
# Kafka Producer
python kafka-producer/src/producer.py

# Spark Streaming
python spark-streaming/src/streaming_app.py

# Streamlit Dashboard
streamlit run streamlit-dashboard/app.py
```

## Installed Packages

The shared environment includes all dependencies for:
- kafka-producer (kafka-python)
- spark-streaming (pyspark, cassandra-driver)
- streamlit-dashboard (streamlit, pandas, plotly, elasticsearch)

## Deactivation

To deactivate the virtual environment:
```bash
deactivate
```</content>
<parameter name="filePath">d:\2025.1_monhoc\big_data_pipeline\venv\README.md