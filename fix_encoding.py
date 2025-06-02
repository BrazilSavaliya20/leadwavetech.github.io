# fix_encoding.py
import os

json_path = os.path.join("data", "blogs.json")

with open(json_path, "rb") as f:
    raw_data = f.read()

# Try decoding using 'utf-16' or fallback to latin1
try:
    decoded = raw_data.decode("utf-16")
except UnicodeDecodeError:
    decoded = raw_data.decode("latin1")

# Save it back as valid UTF-8
with open(json_path, "w", encoding="utf-8") as f:
    f.write(decoded)

print("✅ blogs.json re-encoded to UTF-8")
