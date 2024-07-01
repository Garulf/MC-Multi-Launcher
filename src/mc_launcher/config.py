

def load(path):
    with open(path, "r", encoding='utf-8') as f:
        props = dict(line.strip().split('=', 1) for line in f if '=' in line)
    return props
