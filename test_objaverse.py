import objaverse

uid = "fb9d4da093bd4d1cab6cc29424a3e591"

print("🔎 Looking for the Gaming Mouse...")

objects = objaverse.load_objects(
    uids=[uid]
)

print("✅ Model downloaded!")

print(objects)