#!/bin/bash
# Build script for Drug Dosage Calculator
# Run this in Git Bash from the project directory

echo "=================================="
echo "Building Drug Dosage Calculator"
echo "=================================="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install PyInstaller"
        exit 1
    fi
    echo "✅ PyInstaller installed"
else
    echo "✅ PyInstaller found"
fi

echo ""
echo "🔨 Building executable..."
echo ""

# Clean previous builds
if [ -d "build" ]; then
    rm -rf build
    echo "🗑️  Cleaned old build directory"
fi

if [ -d "dist" ]; then
    rm -rf dist
    echo "🗑️  Cleaned old dist directory"
fi

# Build the executable using spec file
pyinstaller DrugCalculator.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Build successful!"
    echo "=================================="
    echo ""
    echo "📦 Your .exe is located at:"
    echo "   dist/DrugCalculator.exe"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Test the .exe by double-clicking it"
    echo "   2. Run some calculations to verify it works"
    echo "   3. Check that history saves correctly"
    echo ""
    echo "🚀 When ready to release:"
    echo "   - Create a GitHub release (v1.1.1)"
    echo "   - Attach dist/DrugCalculator.exe to the release"
    echo "   - Make repository public"
    echo ""
    
    # Show file size
    if [ -f "dist/DrugCalculator.exe" ]; then
        size=$(du -h "dist/DrugCalculator.exe" | cut -f1)
        echo "📊 .exe file size: $size"
    fi
else
    echo ""
    echo "=================================="
    echo "❌ Build failed"
    echo "=================================="
    echo ""
    echo "Check the error messages above."
    echo "Common issues:"
    echo "  - Missing dependencies"
    echo "  - File path issues"
    echo "  - Python version incompatibility"
    echo ""
fi
