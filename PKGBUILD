
# Maintainer: acidburnmonkey
pkgname=agemo
pkgver=2.1.0
pkgrel=1
pkgdesc="Agemo is a GUI for Hyprpaper, written in Python + Qt6"
arch=('any')
url="https://github.com/acidburnmonkey/agemo"
license=('GLP3')
depends=('uv' 'hyprpaper' 'hyprland')
source=("$pkgname-$pkgver.tar.gz::https://github.com/acidburnmonkey/agemo/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
  cd "$srcdir/$pkgname-$pkgver"

  # Install to /usr/share/agemo
  install -dm755 "$pkgdir/usr/share/agemo"
  cp -r assets agemo.json *.py style.qss pyproject.toml uv.lock agemo.desktop "$pkgdir/usr/share/agemo"

  # Wrapper to install into ~/.local and launch it
  install -Dm755 /dev/stdin "$pkgdir/usr/bin/agemo" <<'EOF'
#!/bin/bash
DEST="$HOME/.local/share/agemo"

if [ ! -d "$DEST" ]; then
  echo "[agemo] Installing to \$DEST"
  mkdir -p "$DEST"
  cp -r /usr/share/agemo/* "$DEST"
  chmod +x "$DEST/agemo.py"

  mkdir -p "$HOME/.local/share/applications"
  cp "$DEST/agemo.desktop" "$HOME/.local/share/applications/"
  sed -i "s|{}|\$HOME|g" "$HOME/.local/share/applications/agemo.desktop"
fi

cd "$DEST"
exec uv run --project . agemo.py "$@"
EOF
}
