# maintainer="uttamkn uttamkn15@gmail.com"

pkgname=mangaplace
pkgver=0.3.0
pkgrel=3
pkgdesc="A CLI tool to download manga."
arch=('x86_64')
url="https://github.com/uttamkn/mangaplace"
license=('MIT')
source=("${pkgname}::https://github.com/uttamkn/mangaplace/releases/download/v${pkgver}/${pkgname}")
sha256sums=('f48327b4b9531a1fe08eb3baeb611d1c95427fb6b4b9ab2f4e051a013749f724')

package() {
  install -Dm755 "$srcdir/$pkgname" "${pkgdir}/usr/bin/${pkgname}"
}
