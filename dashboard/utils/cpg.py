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
    for i in range(0, len(sequence), chunk_size):
        result.append(sequence[i: i + chunk_size])

    return result