
import subprocess
import sys

steps = [
    "src/pipeline.py",
    "src/transform.py"
]

for step in steps:
    print(f"\nRunning: {step}")

    result = subprocess.run(
        [sys.executable, step],
        check=True
    )

print("\nPipeline completed successfully!")
