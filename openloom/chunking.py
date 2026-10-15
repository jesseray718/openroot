def chunk_text(value, size=1000, overlap=100):
    value = value.strip()
    if not value:
        return []
    chunks = []
    start = 0
    while start < len(value):
        end = min(start + size, len(value))
        chunk = value[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(value):
            break
        start = max(0, end - overlap)
    return chunks
