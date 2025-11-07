#!/bin/bash
##
## https://github.com/acidburnmonkey/agemo
##
set -e

# Function to detect package manager
detect_package_manager() {
    if command -v apt > /dev/null 2>&1; then
        echo "apt"
    elif command -v dnf > /dev/null 2>&1; then
        echo "dnf"
    elif command -v yum > /dev/null 2>&1; then
        echo "yum"
    elif command -v pacman > /dev/null 2>&1; then
        echo "pacman"
    elif command -v zypper > /dev/null 2>&1; then
        echo "zypper"
    elif command -v apk > /dev/null 2>&1; then
        echo "apk"
    else
        echo "unknown"
    fi
}

# Check if uv is installed
if command -v uv > /dev/null 2>&1; then
    echo "uv is already installed"
    uv --version
else
    echo "uv is not installed"

    # Detect package manager
    PKG_MANAGER=$(detect_package_manager)

    if [ "$PKG_MANAGER" != "unknown" ]; then
        echo "Detected package manager: $PKG_MANAGER"
        read -p "Would you like to try installing uv via $PKG_MANAGER? (y/n): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Attempting to install via $PKG_MANAGER..."

            case $PKG_MANAGER in
                apt)
                    sudo apt update && sudo apt install -y uv
                    ;;
                dnf)
                    sudo dnf install -y uv
                    ;;
                yum)
                    sudo yum install -y uv
                    ;;
                pacman)
                    sudo pacman -S --noconfirm uv
                    ;;
                zypper)
                    sudo zypper install -y uv
                    ;;
                apk)
                    sudo apk add uv
                    ;;
            esac

            # Check if package manager installation succeeded
            if command -v uv > /dev/null 2>&1; then
                echo "✓ uv installed successfully via $PKG_MANAGER"
                uv --version
            else
                echo "Package not found in $PKG_MANAGER repositories"
                echo "Falling back to official installer..."
            fi
        fi
    fi

    # If uv still not installed, use official installer
    if ! command -v uv > /dev/null 2>&1; then
        echo ""
        echo "Installing uv using official installer from https://astral.sh/uv/install.sh"
        read -p "Would you like to proceed with the official installer? (y/n): " -n 1 -r
        echo

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled - uv is required for agemo"
            exit 1
        fi

        echo "Downloading and running installer..."
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Check if installation was successful
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ uv installation completed"
            echo ""

            # Verify installation
            if command -v uv > /dev/null 2>&1; then
                echo "✓ uv is now available"
                uv --version
            else
                echo "⚠ Installation completed but uv is not yet in your PATH"
                echo ""
                echo "The installer has modified your shell configuration files."
                echo "To use uv immediately, either:"
                echo "  1. Restart your shell/terminal"
                echo "  2. Or run one of these commands based on your shell:"

                # Determine likely install location
                if [ -n "${XDG_BIN_HOME:-}" ]; then
                    INSTALL_DIR="$XDG_BIN_HOME"
                elif [ -n "${XDG_DATA_HOME:-}" ]; then
                    INSTALL_DIR="$XDG_DATA_HOME/../bin"
                else
                    INSTALL_DIR="$HOME/.local/bin"
                fi

                echo ""
                echo "     source $INSTALL_DIR/env          (bash/sh/zsh)"
                echo "     source $INSTALL_DIR/env.fish     (fish)"

                # Try to source it for current session
                if [ -f "$INSTALL_DIR/env" ]; then
                    echo ""
                    echo "Attempting to add uv to current session..."
                    # shellcheck disable=SC1090
                    source "$INSTALL_DIR/env"
                fi
            fi
        else
            echo "✗ uv installation failed"
            exit 1
        fi
    fi
fi

# Final check before installing agemo
if ! command -v uv > /dev/null 2>&1; then
    echo ""
    echo "✗ Error: uv is not available. Cannot proceed with agemo installation."
    echo "Please restart your shell and run this script again."
    exit 1
fi

echo ""
echo "Installing agemo..."


# Install agemo files
mkdir -p "$HOME/.local/share/agemo"
cp -r assets/ agemo.json *.py style.qss pyproject.toml uv.lock "$HOME/.local/share/agemo"

# Install desktop entry
mkdir -p "$HOME/.local/share/applications/"
sed "s|{}|${HOME}|g" agemo.desktop > "$HOME/.local/share/applications/agemo.desktop"

# Make main script executable
chmod +x "$HOME/.local/share/agemo/agemo.py"

echo ""
echo "✓ Done! agemo installed to ~/.local/share/agemo"
echo ""
echo "To run agemo:"
echo " cd ~/.local/share/agemo && uv run agemo.py "
echo ""
echo "Or launch it from your application menu."
