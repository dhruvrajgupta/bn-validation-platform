from pydantic import BaseModel
from typing import List

class SectionData(BaseModel):
    section_name: str
    paragraph: List[str]

class ListSectionData(BaseModel):
    thinking: str
    sections: List[SectionData]

DATA_EXTRACTOR = """\
You are an expert at Data Extraction from HTML Pages.

Task Description: 
Extract all the sections from the provided page of the NCCN Clinical Practitioners Guidelines.
Ensure the extraction is accurate. The output should be a clean, ordered list of section titles as they appear on the page.

After extracting the sections,
1. Extract the important contents of this page using the given input "TEXT CONTENT" and "HTML PAGE CONTENT".
2. Extract the contents in meaningful sentences so that it can be used for clinical data mining.
3. Do not summarize.
4. Output in detail.
5. Segregate into meaningful sections.
6. Ensure accurate data extractions in detailed.
7. "paragraph" should be in markdown representation in ith Output JSON.
8. The output in "paragraph" should depict the exact meaning in the "HTML PAGE CONTENT".

TEXT CONTENT:
```
{text_content}
```

HTML PAGE CONTENT:
```
{html_page}
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
           "section_name": ... ,
           "paragraph": []
       }},
        ...
    ]
}}
</answer>

Before providing the answer in <answer> tags, think step by step in <thinking> tags and analyze every part.
Output inside <answer> tag in JSON format. Only output valid JSON.
DO NOT HALLUCINATE. DO NOT MAKE UP FACTUAL INFORMATION.
"""