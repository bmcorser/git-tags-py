def filter_empty_lines(output):
    return list(filter(bool, output.split('\n')))
