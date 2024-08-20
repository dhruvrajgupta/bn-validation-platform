import os

import unstructured_client
from unstructured_client.models import operations, shared


client = unstructured_client.UnstructuredClient(
    api_key_auth=os.getenv("UNSTRUCTURED_API_KEY"),
    server_url="https://api.unstructured.io/general/v0/general",
)

print(os.getenv("UNSTRUCTURED_API_KEY"))

filename = "/home/dhruv/Desktop/bn-validation-platform/scripts/example-docs/layout-parser-paper-fast.pdf"
with open(filename, "rb") as f:
    data = f.read()

req = operations.PartitionRequest(
    partition_parameters=shared.PartitionParameters(
        files=shared.Files(
            content=data,
            file_name=filename,
        ),
        # --- Other partition parameters ---
        strategy=shared.Strategy.AUTO,
        languages=['eng'],
    ),
)

try:
    res = client.general.partition(request=req)
    print(res.elements[0])
except Exception as e:
    print(e)