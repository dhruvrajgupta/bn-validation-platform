import re

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