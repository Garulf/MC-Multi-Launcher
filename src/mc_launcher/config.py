

def load(path):
    with open(path, "r") as f:
        props = dict(line.strip().split('=', 1) for line in f)
    return props
