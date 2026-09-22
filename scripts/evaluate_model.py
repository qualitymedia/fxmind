"""
CLI to evaluate a trained model version.
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ml.artifacts.saver import ModelArtifactSaver


def main():
    parser = argparse.ArgumentParser(description="Evaluate model version")
    parser.add_argument("--version", type=str, default="gbpusd-m15-v1.0")
    args = parser.parse_args()

    saver = ModelArtifactSaver(base_dir=project_root / "ml" / "artifacts")
    try:
        bundle = saver.load_bundle(args.version)
        print("===============================================")
        print(f" Model Evaluation Summary: {args.version}")
        print("===============================================")
        print(f" Model Type:      {bundle['metadata'].get('model_type')}")
        print(f" Feature Count:   {bundle['schema'].feature_count}")
        print(f" Training Date:   {bundle['metadata'].get('created_at')}")
        print("===============================================")
    except Exception as e:
        print(f"[ERROR] Failed to load model version '{args.version}': {e}")


if __name__ == "__main__":
    main()
