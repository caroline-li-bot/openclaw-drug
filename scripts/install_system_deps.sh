#!/bin/bash
# AutoDock Vina and related system dependencies installation script for Ubuntu/Debian
# Usage: sudo ./scripts/install_system_deps.sh

set -e

echo "=== Installing system dependencies for DrugClaw AutoDock Vina ===\n"

# Update package list
apt update

# Install openbabel - for SMILES to 3D conformation
echo -e "\n[1/5] Installing OpenBabel..."
apt install -y openbabel

# Install AutoDock Vina
echo -e "\n[2/5] Installing AutoDock Vina..."
apt install -y autodock-vina

# Install MGLTools for prepare_receptor/prepare_ligand
echo -e "\n[3/5] Installing MGLTools..."
# MGLTools is not in default repo, we need to download it
cd /tmp
wget https://ccsb.scripps.edu/download/5267/ -O mgltools.tar.gz
tar xzf mgltools.tar.gz
cd mgltools_x86_64Linux2_*
./install.sh
# Add to PATH
echo 'export PATH=$PATH:/usr/local/mgltools*/bin' >> ~/.bashrc
export PATH=$PATH:/usr/local/mgltools*/bin

# Install other useful utilities
echo -e "\n[4/5] Installing other utilities..."
apt install -y python3-pip wget tar gzip

# Verify installation
echo -e "\n[5/5] Verifying installation..."
echo ""

if command -v vina &> /dev/null; then
    echo "✅ AutoDock Vina: OK"
    vina --version
else
    echo "❌ AutoDock Vina: FAILED"
fi

if command -v obabel &> /dev/null; then
    echo "✅ OpenBabel: OK"
else
    echo "❌ OpenBabel: FAILED"
fi

if command -v prepare_receptor &> /dev/null; then
    echo "✅ prepare_receptor: OK"
else
    echo "⚠️  prepare_receptor: NOT FOUND - check MGLTools installation"
fi

echo -e "\n=== Installation complete ==="
echo "Please restart your shell or run: source ~/.bashrc"
