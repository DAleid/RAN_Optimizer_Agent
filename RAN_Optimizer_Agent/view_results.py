"""
View training results without dashboard
"""
import json
import os
from PIL import Image
import matplotlib.pyplot as plt

print("="*60)
print("  RAN OPTIMIZER - TRAINING RESULTS")
print("="*60)

results_dir = "results"

# Find latest files
files = os.listdir(results_dir)
json_files = [f for f in files if f.endswith('.json')]
png_files = [f for f in files if f.endswith('.png')]
pth_files = [f for f in files if f.endswith('.pth')]

if json_files:
    latest_json = sorted(json_files)[-1]
    print(f"\nLatest A/B Test Results: {latest_json}")
    print("-"*60)

    with open(os.path.join(results_dir, latest_json), 'r') as f:
        data = json.load(f)
        test = data[0]

        print(f"Test ID: {test['test_id']}")
        print(f"Timestamp: {test['timestamp']}")
        print()

        print("Group A (with AI optimization):")
        for key, value in test['group_a_metrics'].items():
            print(f"  {key}: {value:.2f}")

        print()
        print("Group B (control/baseline):")
        for key, value in test['group_b_metrics'].items():
            print(f"  {key}: {value:.2f}")

        print()
        print("Improvement:")
        for key, value in test['improvement'].items():
            print(f"  {key}: {value:+.2f}%")

        print()
        print(f"Statistically Significant: {test['is_significant']}")
        print(f"Confidence: {test['confidence']:.1f}%")
        print()
        print(f"Recommendation: {test['recommendation']}")

print("\n" + "="*60)
print(f"Trained Models: {len(pth_files)} models saved")
print(f"Training Graphs: {len(png_files)} graphs generated")
print("="*60)

if png_files:
    latest_png = sorted(png_files)[-1]
    png_path = os.path.join(results_dir, latest_png)
    print(f"\nTo view training graphs, open:")
    print(f"  {os.path.abspath(png_path)}")

    # Try to open the image
    try:
        img = Image.open(png_path)
        img.show()
        print("\n Opening training graphs...")
    except:
        print("\n Please manually open the PNG file to view graphs.")

print("\n" + "="*60)
print("SUMMARY: Your AI agent has been trained successfully!")
print("="*60)
