import os, json

import unstructured_client
from unstructured_client.models import operations, shared


client = unstructured_client.UnstructuredClient(
    api_key_auth=os.getenv("UNSTRUCTURED_API_KEY"),
    server_url="https://api.unstructured.io/general/v0/general",
)

# print(os.getenv("UNSTRUCTURED_API_KEY"))

# filename = "/home/dhruv/Desktop/bn-validation-platform/scripts/example-docs/layout-parser-paper-fast.pdf"
# with open(filename, "rb") as f:
#     data = f.read()

# req = operations.PartitionRequest(
#     partition_parameters=shared.PartitionParameters(
#         files=shared.Files(
#             content=data,
#             file_name=filename,
#         ),
#         # --- Other partition parameters ---
#         strategy=shared.Strategy.AUTO,
#         languages=['eng'],
#     ),
# )

# try:
#     res = client.general.partition(request=req)
#     print(res.elements[0])
# except Exception as e:
#     print(e)

input_filepath = "/home/dhruv/Desktop/bn-validation-platform/scripts/example-docs/layout-parser-paper-fast.pdf"
output_filepath = "/home/dhruv/Desktop/bn-validation-platform/scripts/example-docs/layout-parser-paper-fast.json"

with open(input_filepath, "rb") as f:
    files = shared.Files(
        content=f.read(),
        file_name=input_filepath
    )

req = operations.PartitionRequest(
    shared.PartitionParameters(
        files=files,
        split_pdf_page=True,
        split_pdf_allow_failed=True,
        split_pdf_concurrency_level=15
    )
)

try:
    res = client.general.partition(request=req)
    element_dicts = [element for element in res.elements]
    json_elements = json.dumps(element_dicts, indent=2)

    # Print the processed data.
    print(json_elements)

    # Write the processed data to a local file.
    with open(output_filepath, "w") as file:
        file.write(json_elements)
except Exception as e:
    print(e)