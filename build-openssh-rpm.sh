#!/usr/bin/env bash
export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
TZ='UTC'; export TZ

/sbin/ldconfig

hostnamectl --static set-hostname 'x86-034.build.eng.bos.redhat.com'
systemctl restart systemd-hostnamed.service
sleep 10

cd "$(dirname "$0")"

set -e

if ! grep -q -i '^1:.*docker' /proc/1/cgroup; then
    echo
    echo ' Not in a container!'
    echo
    exit 1
fi

bash ./.dl-openssh.sh
bash build-libcbor-ssl111-fido2.sh
_tmp_dir="$(mktemp -d)"
cp -pf openssh.spec "${_tmp_dir}"/
cp -pf openssh-*.tar* "${_tmp_dir}"/
sleep 1
rm -fr openssh-*.tar*
cd "${_tmp_dir}"

_openssh_ver="$(ls -1 openssh-*.tar* | sort -V | tail -n 1 | cut -d- -f2 | sed 's|\.tar.*||g')"
sed "s/%global ver .*/%global ver ${_openssh_ver}/g" -i openssh.spec
tar -xf "openssh-${_openssh_ver}".tar.gz

cd "openssh-${_openssh_ver}"/
rm -rf ChangeLog
sed -n '/%changelog/,//p' contrib/redhat/openssh.spec  > ChangeLog
cat ../openssh.spec > contrib/redhat/openssh.spec
sed "s/%global rel .*%{?dist}/%global rel $(date -u +%Y%m%d)%{?dist}/g" -i contrib/redhat/openssh.spec
cat ChangeLog >> contrib/redhat/openssh.spec
rm -f ../openssh.spec
sed 's@%global no_x11_askpass 0@%global no_x11_askpass 1@g' -i contrib/redhat/openssh.spec
sed 's@%global no_gnome_askpass 0@%global no_gnome_askpass 1@g' -i contrib/redhat/openssh.spec
sed 's/BuildRequires: openssl-devel/#BuildRequires: openssl-devel/g' -i contrib/redhat/openssh.spec

#sed 's/%configure \\/%configure \\\n\t--with-ssl-dir=\/usr\/local\/openssl-1.1.1 \\/g' -i contrib/redhat/openssh.spec

cp -fr contrib/redhat/openssh.spec ../
cd ..

sleep 2
tar -zcf "openssh-${_openssh_ver}".tar.gz "openssh-${_openssh_ver}"
sleep 2

rm -fr ~/rpmbuild
rm -fr "openssh-${_openssh_ver}"
sleep 1

install -m 0755 -d ~/rpmbuild/SOURCES
cp -pfr "openssh-${_openssh_ver}".tar.gz ~/rpmbuild/SOURCES/
cp -pfr openssh.spec ~/rpmbuild/SOURCES/
sleep 1

############################################################################
cd /tmp
rm -fr "${_tmp_dir}"
rpmbuild -v -ba ~/rpmbuild/SOURCES/openssh.spec

rm -fr /tmp/_output
install -m 0755 -d /tmp/_output/openssh
find ~/rpmbuild/RPMS/ -type f -iname '*.rpm' -exec /bin/cp -pfr '{}' /tmp/_output/openssh/ \;
sleep 1
cd /tmp/_output/openssh/
sha256sum *.rpm > sha256sums.txt

cd /tmp
/sbin/ldconfig
exit

