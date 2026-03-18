import hashlib

def tenant_color(name):
    colors = [
        "badge-info",
        "badge-warning",
        "badge-success",
        "badge-danger",
        "badge-purple",
        "badge-pink",
        "badge-cyan",
        "badge-orange",
    ]

    if not name:
        return "badge-secondary"

    hash_val = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return colors[hash_val % len(colors)]