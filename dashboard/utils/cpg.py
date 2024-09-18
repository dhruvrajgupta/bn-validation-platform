import re
from openai import OpenAI

def split_sequence(sequence, chunk_size):
    """
    Split a sequence into chunks of a given size.

    Parameters
    ----------
    sequence : iterable
        The sequence to be split.
    chunk_size : int
        The size of each chunk.

    Returns
    -------
    list
        A list of chunks of the given size.
    """
    result = []
    result.append([])
    for i in range(0, len(sequence), chunk_size):
        result.append(sequence[i: i + chunk_size])

    return result

def format_annotated_text(text):

    """
    Format annotated text into a list of tuples, where each tuple contains the content of
    either a tag or plain text and the corresponding label.

    Parameters
    ----------
    text : str
        The annotated text to be formatted.

    Returns
    -------
    list
        A list of tuples, where each tuple contains the content of either a tag or plain text
        and the corresponding label.
    """
    tag_labels = {
        'C': 'cause',
        'E': 'effect',
        'A': 'action',
        'CO': 'conditional'
    }

    # Regex pattern to match any of the tags and capture their content
    pattern = r'(<(?P<tag>C|E|A|CO)>.*?</\2>)|([^<]+)'

    result = []

    for match in re.finditer(pattern, text):
        if match.group('tag'):
            tag = match.group('tag')
            content = re.sub(r'</?.*?>', '', match.group(0)).strip()  # Remove the tags
            result.append((content, tag_labels[tag]))
        else:
            content = match.group(0).strip()
            if content:
                result.append(f" {content} ")

    return result


def ask_llm(prompt: str, stream=False):
    """
    Ask the LLM a question and print the response.

    Parameters
    ----------
    prompt : str
        The question to ask the LLM.
    stream : bool, optional
        If True, stream the response from the LLM as it is generated. If False, wait for the
        entire response to be generated before printing it. Defaults to False.

    Returns
    -------
    str
        The response from the LLM.
    """

    model_name = "gpt-4o-mini"
    temperature = 0

    client = OpenAI(
        # Defaults to os.environ.get("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        stream=stream
    )

    print(f"START OF LLM RESPONSE: \n{'-'*20}\n")

    if stream:
        llm_response = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                llm_response += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end='', flush=True)

    else:
        llm_response = response.choices[0].message.content
        print(llm_response)

    print(f"\n\nEND OF LLM RESPONSE\n{'-'*50}\n")

    return llm_response