#!/bin/bash

# Evaluation Runner - Runs tests, generates comparison report, and opens in browser
# Usage: 
#   ./run_eval.sh                           # Run all configured models
#   ./run_eval.sh gpt-4o                    # Run single model
#   ./run_eval.sh gpt-4o gpt-4o-mini        # Run multiple specific models

set -e  # Exit on error

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Go to backend directory (two levels up from scripts directory)
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Activate pyenv environment
eval "$(pyenv init -)"
pyenv activate sarj

cd "$BACKEND_DIR"

echo "🚀 Starting Evaluation Pipeline"
echo "================================"

# Determine what to run
if [ $# -eq 0 ]; then
    # No arguments - run all models
    echo "📊 Running comparison evaluation for all configured models..."
    python evaluations/scripts/run_development_eval.py --compare-models
else
    # Run evaluation for each specified model
    echo "📊 Running evaluation for $# model(s): $@"
    echo ""
    
    for model in "$@"; do
        echo "▶️  Evaluating: $model"
        python evaluations/scripts/run_development_eval.py --model "$model"
        echo "✅ Completed: $model"
        echo ""
    done
    
    echo "ℹ️  All specified models evaluated. Generating comparison..."
fi

echo ""
echo "✅ Evaluation complete!"
echo ""

# Generate comparison report
echo "📈 Generating comparison report..."
python evaluations/scripts/generate_comparison_report.py

# Find the latest comparison report
LATEST_REPORT=$(ls -t evaluations/results/comparison_*.html | head -1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ No comparison report found!"
    exit 1
fi

echo ""
echo "✅ Report generated: $LATEST_REPORT"
echo ""

# Open in browser
echo "🌐 Opening report in browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$LATEST_REPORT"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$LATEST_REPORT"
else
    echo "⚠️  Please open manually: file://$(pwd)/$LATEST_REPORT"
fi

echo ""
echo "🎉 Done! The comparison report is now open in your browser."
echo "   You can click on any model card to see detailed test results."
