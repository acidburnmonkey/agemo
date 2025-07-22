
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

  # Install source files for runtime (keep original .desktop here)
  install -dm755 "$pkgdir/usr/share/agemo"
  cp -r assets agemo.json *.py style.qss pyproject.toml uv.lock agemo.desktop "$pkgdir/usr/share/agemo"

  # Install icon
  install -Dm644 assets/agemo.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/agemo.svg"

  # Create launcher script in /usr/bin that uses uv
  install -Dm755 /dev/stdin "$pkgdir/usr/bin/agemo" <<'EOF'
#!/bin/bash
exec uv run --project /usr/share/agemo agemo.py "$@"
EOF

  # Generate a proper system .desktop file pointing to /usr/share/agemo
  install -Dm644 /dev/stdin "$pkgdir/usr/share/applications/agemo.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=2.1.0
Name=Agemo
Comment=Wallpaper GUI
Path=/usr/share/agemo
Exec=/usr/bin/env uv run --project /usr/share/agemo agemo.py
Icon=agemo
Terminal=false
Keywords=wallpaper;hyprpaper
EOF
}
