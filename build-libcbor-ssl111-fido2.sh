#!/usr/bin/env bash
export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
TZ='UTC'; export TZ

umask 022

CFLAGS='-O2 -fexceptions -g -grecord-gcc-switches -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -fstack-protector-strong -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection'
export CFLAGS
CXXFLAGS='-O2 -fexceptions -g -grecord-gcc-switches -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -fstack-protector-strong -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection'
export CXXFLAGS
LDFLAGS='-Wl,-z,relro -Wl,--as-needed -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld'
export LDFLAGS

/sbin/ldconfig

set -e

if ! grep -q -i '^1:.*docker' /proc/1/cgroup; then
    echo
    echo ' Not in a container!'
    echo
    exit 1
fi

_tmp_dir="$(mktemp -d)"
cd "${_tmp_dir}"

_install_zlib () {
    set -e
    _tmp_dir="$(mktemp -d)"
    cd "${_tmp_dir}"
    _zlib_ver="$(wget -qO- 'https://www.zlib.net/' | grep -i 'HREF="zlib-[0-9].*\.tar\.' | sed 's|"|\n|g' | grep '^zlib-' | grep -ivE 'alpha|beta|rc' | sed -e 's|zlib-||g' -e 's|\.tar.*||g' | sort -V | uniq | tail -n 1)"
    wget -q -c -t 9 -T 9 "https://zlib.net/zlib-${_zlib_ver}.tar.xz"
    sleep 1
    tar -xf "zlib-${_zlib_ver}.tar.xz"
    sleep 1
    rm -f zlib-*.tar*
    cd "zlib-${_zlib_ver}"
    ./configure --prefix=/usr --libdir=/usr/lib64 --includedir=/usr/include --sysconfdir=/etc --64
    sleep 1
    make all
    rm -f /usr/lib64/libz.*
    sleep 1
    make install
    sleep 1
    cd /tmp
    rm -fr "${_tmp_dir}"
    /sbin/ldconfig >/dev/null 2>&1
}
_install_zlib

CC=gcc
export CC
CXX=g++
export CXX

_install_libedit () {
    set -e
    _tmp_dir="$(mktemp -d)"
    cd "${_tmp_dir}"
    _libedit_ver="$(wget -qO- 'https://www.thrysoee.dk/editline/' | grep libedit-[1-9].*\.tar | sed 's|"|\n|g' | grep '^libedit-[1-9]' | sed -e 's|\.tar.*||g' -e 's|libedit-||g' | sort -V | uniq | tail -n 1)"
    wget -q -c -t 9 -T 9 "https://www.thrysoee.dk/editline/libedit-${_libedit_ver}.tar.gz"
    sleep 1
    tar -xf libedit-${_libedit_ver}.tar.*
    sleep 1
    rm -f libedit-*.tar*
    cd libedit-*
    sed -i "s/lncurses/ltinfo/" configure
    sleep 1
    ./configure \
    --build=x86_64-linux-gnu \
    --host=x86_64-linux-gnu \
    --prefix=/usr \
    --libdir=/usr/lib64 \
    --includedir=/usr/include \
    --sysconfdir=/etc \
    --enable-shared --enable-static \
    --enable-widec
    sleep 1
    make all
    rm -f /usr/lib64/libedit.*
    sleep 1
    make install
    sleep 1
    cd /tmp
    rm -fr "${_tmp_dir}"
    /sbin/ldconfig >/dev/null 2>&1
}
_install_libedit


_install_libcbor () {
    set -e
    _tmp_dir="$(mktemp -d)"
    cd "${_tmp_dir}"
    _libcbor_ver="$(wget -qO- 'https://github.com/PJK/libcbor/tags' | grep -i 'href="/PJK/libcbor/archive/refs/tags/.*.tar.gz' | sed 's|"|\n|g' | grep '^/PJK/libcbor/archive/refs/tags' | sed -e 's|.*tags/v||g' -e 's|\.tar.*||g' | sort -V | uniq | tail -n 1)"
    wget -q -c -t 9 -T 9 "https://github.com/PJK/libcbor/archive/v${_libcbor_ver}/libcbor-${_libcbor_ver}.tar.gz"
    sleep 1
    tar -xf "libcbor-${_libcbor_ver}.tar.gz"
    sleep 1
    rm -f libcbor*.tar*
    cd "libcbor-${_libcbor_ver}"
    /usr/bin/cmake \
    -S "." \
    -B "build" \
    -DCMAKE_BUILD_TYPE='Release' \
    -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=/usr \
    -DINCLUDE_INSTALL_DIR:PATH=/usr/include \
    -DLIB_INSTALL_DIR:PATH=/usr/lib64 \
    -DSYSCONF_INSTALL_DIR:PATH=/etc \
    -DSHARE_INSTALL_PREFIX:PATH=/usr/share \
    -DLIB_SUFFIX=64 \
    -DBUILD_SHARED_LIBS:BOOL=ON
    /usr/bin/cmake --build "build"  --verbose
    rm -f /usr/include/cbor.h
    rm -f /usr/lib64/pkgconfig/libcbor.pc
    rm -f /usr/lib64/libcbor.*
    rm -fr /usr/include/cbor
    /usr/bin/cmake --install "build"
    sleep 1
    cd /tmp
    rm -fr "${_tmp_dir}"
    /sbin/ldconfig >/dev/null 2>&1
}
_install_libcbor


_install_ssl111 () {
    LDFLAGS=''
    LDFLAGS='-Wl,-z,relro -Wl,--as-needed -Wl,-z,now -Wl,-rpath,\$$ORIGIN'
    export LDFLAGS
    set -e
    _tmp_dir="$(mktemp -d)"
    cd "${_tmp_dir}"
    _ssl_ver="$(wget -qO- 'https://www.openssl.org/source/' | grep '1.1.1' | sed 's/">/ /g' | sed 's/<\/a>/ /g' | awk '{print $3}' | grep '\.tar.gz' | sed -e 's|openssl-||g' -e 's|\.tar.*||g' | sort -V | tail -n 1)"
    wget -q -c -t 9 -T 9 "https://www.openssl.org/source/openssl-${_ssl_ver}.tar.gz"
    sleep 1
    tar -xf "openssl-${_ssl_ver}.tar.gz"
    sleep 1
    rm -f openssl*.tar.gz
    cd openssl-*
    sleep 2
    ./Configure \
    --prefix=/usr \
    --libdir=/usr/lib64 \
    --openssldir=/etc/pki/tls \
    enable-tls1_3 threads shared \
    enable-camellia enable-seed enable-rfc3779 \
    enable-sctp enable-cms enable-md2 enable-rc5 \
    no-mdc2 no-ec2m \
    no-sm2 no-sm3 no-sm4 \
    enable-ec_nistp_64_gcc_128 linux-x86_64 \
    '-DDEVRANDOM="\"/dev/urandom\""'
    sleep 1
    sed 's@engines-1.1@engines@g' -i Makefile
    make all
    rm -f /usr/lib64/pkgconfig/openssl.pc
    rm -f /usr/lib64/pkgconfig/libssl.pc
    rm -f /usr/lib64/pkgconfig/libcrypto.pc
    rm -fr /usr/include/openssl
    sleep 1
    make install_sw
    sleep 1
    cd ..
    rm -fr openssl*
    cd /tmp
    rm -fr "${_tmp_dir}"
    /sbin/ldconfig >/dev/null 2>&1
}
#LDFLAGS='-Wl,-z,relro -Wl,--as-needed -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld -Wl,-rpath,/usr/lib64/openssh/private'
_install_ssl111

#LDFLAGS='-Wl,-z,relro -Wl,--as-needed -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld'
#export LDFLAGS

_install_fido2 () {
    LDFLAGS=''
    LDFLAGS='-Wl,-z,relro -Wl,--as-needed -Wl,-z,now -Wl,-rpath,\$$ORIGIN'
    export LDFLAGS
    set -e
    _tmp_dir="$(mktemp -d)"
    cd "${_tmp_dir}"
    _libfido2_ver="$(wget -qO- 'https://developers.yubico.com/libfido2/Releases/' | grep -i 'a href="libfido2-.*\.tar' | sed 's|"|\n|g' | grep -iv '\.sig' | grep -i '^libfido2' | sed -e 's|libfido2-||g' -e 's|\.tar.*||g' | sort -V | uniq | tail -n 1)"
    wget -q -c -t 9 -T 9 "https://developers.yubico.com/libfido2/Releases/libfido2-${_libfido2_ver}.tar.gz"
    sleep 1
    tar -xf "libfido2-${_libfido2_ver}.tar.gz"
    sleep 1
    rm -f libfido*.tar*
    cd "libfido2-${_libfido2_ver}"
    PKG_CONFIG_PATH=/usr/lib64/pkgconfig \
    cmake -S . -B build -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE:STRING='Debug' \
    -DCMAKE_INSTALL_SO_NO_EXE=0 -DUSE_PCSC=ON \
    -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib64 \
    -DCMAKE_BUILD_RPATH='/usr/lib64/openssh/private'
    /usr/bin/cmake --build "build"  --verbose
    rm -f /usr/lib64/libfido2.*
    rm -f /usr/include/fido.h
    rm -fr /usr/include/fido
    sed '/NEW_RPATH ""/s|NEW_RPATH ""|NEW_RPATH "/usr/lib64/openssh/private"|g' -i build/src/cmake_install.cmake
    sed '/OLD_RPATH "/s|:"|"|g' -i build/src/cmake_install.cmake
    /usr/bin/cmake --install "build"
    sleep 1
    cd /tmp
    rm -fr "${_tmp_dir}"
    /sbin/ldconfig >/dev/null 2>&1
}
_install_fido2

cd /tmp
rm -fr "${_tmp_dir}"
echo
echo ' done'
echo
exit

