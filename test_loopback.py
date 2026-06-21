import soundcard as sc

# List all speakers (output devices)
speakers = sc.all_speakers()
print("Available speakers:")
for speaker in speakers:
    print(f"  - {speaker.name} (ID: {speaker.id})")

# Try to get the default speaker's loopback
default_speaker = sc.default_speaker()
print(f"\nDefault speaker: {default_speaker.name}")

# Check if loopback is available
try:
    loopback = default_speaker.loopback()
    print(f"Loopback available: {loopback.name}")
except Exception as e:
    print(f"Loopback not available: {e}")