import io
from io import BytesIO

# import pandas as pd
from google.cloud import storage


# class upload:
# def upload_blob(source_file_name, destination_blob_name):
storage_client = storage.Client.from_service_account_json(
    "src/diesel-monitor-421118-886ca24cb600.json"
)
destination_blob_name = "events/04/evento4.jpg"
bucket = storage_client.get_bucket("tickpass-assets")
blob = bucket.blob(destination_blob_name)

with open("src/cursomaximus.jpg", "rb") as f:
    teste = blob.upload_from_file(f)
    teste = blob.upload_from_string

print(blob)
print(teste)

return 'https://storage.googleapis.com/tickpass-assets/' + destination_blob_name
