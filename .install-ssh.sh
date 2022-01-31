#!/usr/bin/env bash
export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
TZ='UTC'; export TZ

cd "$(dirname "$0")"

_VERIFY="$(ls -1 openssh/openssh-server-*.rpm 2>/dev/null | grep '^openssh/openssh-server-')"

if [[ -z "${_VERIFY}" ]]; then
    echo
    echo '  no file:  openssh/openssh-server-*.rpm'
    echo
    exit 1
fi

cd openssh

sha256sum --check sha256sums.txt 2>/dev/null; _rc_status="$?"
if [[ ${_rc_status} != "0" ]]; then
    echo
    printf '\033[01;31m%s\033[m\n' 'Checksum failed' 'Aborted'
    echo
fi

service sshd stop >/dev/null 2>&1 || : 
chkconfig --del sshd >/dev/null 2>&1 || : 
systemctl disable sshd.service >/dev/null 2>&1 || : 
systemctl stop sshd.service >/dev/null 2>&1 || : 
rpm -evh --nodeps openssh openssh-clients openssh-server
echo
rm -f /etc/pam.d/sshd
rm -f /etc/pam.d/sshd.*
rm -fr /usr/libexec/openssh
rm -fr /etc/systemd/system/sshd.service.d
rm -fr /etc/sysconfig/sshd
rm -fr /etc/ssh

yum -y install openssh-[1-9]*.rpm openssh-clients-*.rpm
yum -y install openssh-server-*.rpm

cd /tmp
systemctl daemon-reload >/dev/null 2>&1 || : 
echo
rpm -qa | grep -i '^openssh-'
echo
exit

