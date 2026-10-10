# Canvas Data 2 (DAP) Ingestion Workflow in Microsoft Fabric
# Pattern: Automated daily sync using the official DAP client into OneLake Delta

import os
from instructure_dap.client import DAPClient
from pyspark.sql.functions import col, current_timestamp, lit, row_number
from pyspark.sql.window import Window

# Step 1: Initialize the DAP client using environment credentials
# (In production Fabric notebooks, pull these securely via Key Vault / mssparkutils)
dap_client = DAPClient(
    base_url="https://api-gateway.instructure.com",
    client_id=os.getenv("DAP_CLIENT_ID"),
    client_secret=os.getenv("DAP_CLIENT_SECRET")
)

# Step 2: Download the latest snapshot files for heavy LMS entities
target_table = "submissions"
output_directory = f"/lakehouse/default/Files/raw_dap/{target_table}"

# Stream snapshot partitions locally to Lakehouse storage to avoid driver memory pressure
dap_client.download_table(
    namespace="canvas",
    table_name=target_table,
    output_directory=output_directory,
    file_format="json"
)

# Step 3: Ingest into Spark and land raw records into Bronze Delta
df_raw = spark.read.json(f"Files/raw_dap/{target_table}/*.json")

df_bronze = (
    df_raw
    .withColumn("ingested_at", current_timestamp())
    .withColumn("source_system", lit("canvas_dap"))
)

df_bronze.write.format("delta").mode("append").saveAsTable(f"bronze_canvas_{target_table}")

# Step 4: Deduplicate across overlapping partitions to keep the latest state for Silver
window_spec = Window.partitionBy("id").orderBy(col("updated_at").desc())

df_silver = (
    df_bronze
    .withColumn("row_rank", row_number().over(window_spec))
    .filter(col("row_rank") == 1)
    .drop("row_rank")
)

# Stage clean, query-ready records for analyst reporting
df_silver.write.format("delta").mode("overwrite").saveAsTable(f"silver_canvas_{target_table}")
