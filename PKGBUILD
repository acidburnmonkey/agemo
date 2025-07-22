
# Maintainer: acidburnmonkey
pkgname=agemo
pkgver=2.1.0
pkgrel=1
pkgdesc="Agemo is a GUI for Hyprpaper, written in Python + Qt6"
arch=('any')
url="https://github.com/acidburnmonkey/agemo"
license=('GLP3')
depends=('uv' 'hyprpaper' 'hyprland')
source=("$pkgname-$pkgver.tar.gz::https://github.com/acidburnmonkey/agemo/archive/refs/tags/$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
  cd "$srcdir/$pkgname-$pkgver"

  install -dm755 "$pkgdir/usr/share/agemo"
  cp -r assets agemo.json *.py style.qss pyproject.toml uv.lock agemo.desktop "$pkgdir/usr/share/agemo"

  install -Dm644 assets/agemo.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/agemo.svg"

  install -Dm755 /dev/stdin "$pkgdir/usr/bin/agemo" <<'EOF'
#!/bin/bash
PROJECT_DIR="/usr/share/agemo"
VENV_DIR="$HOME/.cache/agemo/venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "[agemo] Creating virtual environment in $VENV_DIR"
  mkdir -p "$VENV_DIR"
  uv venv --venv "$VENV_DIR" "$PROJECT_DIR"
  uv pip install --venv "$VENV_DIR" "$PROJECT_DIR"
fi

exec uv venv run --venv "$VENV_DIR" -- python "$PROJECT_DIR/agemo.py" "$@"
EOF

  # Generate .desktop file for system launcher
  install -Dm644 /dev/stdin "$pkgdir/usr/share/applications/agemo.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=${pkgver}
Name=Agemo
Comment=Wallpaper GUI for Hyprpaper
Path=/usr/share/agemo
Exec=/usr/bin/agemo
Icon=agemo
Terminal=false
Keywords=wallpaper;hyprpaper
Categories=Utility;
EOF
}

