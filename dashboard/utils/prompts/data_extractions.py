from pydantic import BaseModel
from typing import List

class SectionData(BaseModel):
    section_name: str
    paragraph: str

class ListSectionData(BaseModel):
    thinking: str
    sections: List[SectionData]

# 9. Add another section for superscripts informations present within the page for their relevant sections.
DATA_EXTRACTOR = """\
You are an expert at Data Extraction and Merging.

Task Description: 
1. Extract the contents in meaningful sentences so that it can be used for clinical data mining.
2. Extract all the sections from "SOURCE1".
3. Extract all the text accurately from "SOURCE1".
4. Extract all the sections from "SOURCE2".
5. Extract all the text accurately from "SOURCE2".
6. Merge the text contents of the two data sources "SOURCE1" and "SOURCE2"
7. Ensure the extraction is accurate and in detail.
8. Do not summarize.
9. Output in detail.
10. Segregate into meaningful sections.
11. "paragraph" should be in markdown representation in ith Output JSON.
12. The output in "paragraph" should depict the exact meaning in the "SOURCE1" and "SOURCE2".
13. Do not output repeated content.

SOURCE1:
```
{chunk_data_content}
```

SOURCE2:
```
{html_hr_content}
```

DESIRED OUTPUT FORMAT:
<thinking>
...
</thinking>
<answer>
{{
    "thinking": "...",
    "sections": [
       {{
           "section_name": "..." ,
           "paragraph": "..."
       }},
        ...
    ]
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""


HTML_TO_READABLE_FORMAT = """\
You are an expert Data Extractor.
You will be given a NCCN Clinical Practitioner's Guidelines page which is converted in HTML5 format.
Your task is to convert this HTML format to markdown format which is human readable and understandable format.
Ensure the extraction is accurate and in detail.

HTML PAGE CONTENT:
```
{html_page}
```
"""