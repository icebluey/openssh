%global dist .el7

%global ver 9.0p1
%global rel 1%{?dist}

# Do we want SELinux & Audit
%if 0%{?!noselinux:1}
%global WITH_SELINUX 1
%else
%global WITH_SELINUX 0
%endif

# OpenSSH privilege separation requires a user & group ID
%global sshd_uid    74
%global sshd_gid    74

# Version of ssh-askpass
%global aversion 1.2.4.1

# Do we want to disable building of x11-askpass? (1=yes 0=no)
%global no_x11_askpass 0

# Do we want to disable building of gnome-askpass? (1=yes 0=no)
%global no_gnome_askpass 0

# Do we want to link against a static libcrypto? (1=yes 0=no)
%global static_libcrypto 0

# Do we want smartcard support (1=yes 0=no)
%global scard 0

# Use GTK2 instead of GNOME in gnome-ssh-askpass
%global gtk2 1

# Use build6x options for older RHEL builds
# RHEL 7 not yet supported
%if 0%{?rhel} > 6
%global build6x 0
%else
%global build6x 1
%endif

%if 0%{?fedora} >= 26
%global compat_openssl 1
%else
%global compat_openssl 0
%endif

# Do we want kerberos5 support (1=yes 0=no)
%global kerberos5 1

# Do we want libedit support
%global libedit 1

# Reserve options to override askpass settings with:
# rpm -ba|--rebuild --define 'skip_xxx 1'
%{?skip_x11_askpass:%global no_x11_askpass 1}
%{?skip_gnome_askpass:%global no_gnome_askpass 1}

# Add option to build without GTK2 for older platforms with only GTK+.
# RedHat <= 7.2 and Red Hat Advanced Server 2.1 are examples.
# rpm -ba|--rebuild --define 'no_gtk2 1'
%{?no_gtk2:%global gtk2 0}

# Is this a build for RHL 6.x or earlier?
%{?build_6x:%global build6x 1}

# If this is RHL 6.x, the default configuration has sysconfdir in /usr/etc.
%if %{build6x}
%global _sysconfdir /etc
%endif

# Options for static OpenSSL link:
# rpm -ba|--rebuild --define "static_openssl 1"
%{?static_openssl:%global static_libcrypto 1}

# Options for Smartcard support: (needs libsectok and openssl-engine)
# rpm -ba|--rebuild --define "smartcard 1"
%{?smartcard:%global scard 1}

# Is this a build for the rescue CD (without PAM, with MD5)? (1=yes 0=no)
%global rescue 0
%{?build_rescue:%global rescue 1}

# Turn off some stuff for resuce builds
%if %{rescue}
%global kerberos5 0
%global libedit 0
%endif


Name:           openssh
Version:        %{ver}
%if %{rescue}
Release:        %{rel}rescue
%else
Release:        %{rel}
%endif
Summary:        The OpenSSH implementation of SSH protocol version 2.

Group:          Applications/Internet
License:        BSD
URL:            https://www.openssh.com/portable.html
Source0:        https://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-%{version}.tar.gz
#Source1:        http://www.jmknoble.net/software/x11-ssh-askpass/x11-ssh-askpass-%{aversion}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Obsoletes: ssh
%if %{build6x}
PreReq: initscripts >= 5.00
%else
Requires: initscripts >= 5.20
%endif
BuildRequires: perl
%if %{compat_openssl}
BuildRequires: compat-openssl10-devel
%else
BuildRequires: openssl-devel >= 1.0.1
BuildRequires: openssl-devel < 1.1
%endif
BuildRequires: /bin/login
%if ! %{build6x}
BuildRequires: glibc-devel, pam
%else
BuildRequires: /usr/include/security/pam_appl.h
%endif
%if ! %{no_x11_askpass}
BuildRequires: /usr/include/X11/Xlib.h
# Xt development tools
BuildRequires: libXt-devel
# Provides xmkmf
BuildRequires: imake
# Rely on relatively recent gtk
BuildRequires: gtk2-devel
%endif
%if ! %{no_gnome_askpass}
BuildRequires: pkgconfig
%endif
BuildRequires: pam-devel
BuildRequires: systemd-devel
%if %{kerberos5}
BuildRequires: krb5-devel
BuildRequires: krb5-libs
%endif
%if %{libedit}
BuildRequires: libedit-devel ncurses-devel
%endif
%if %{WITH_SELINUX}
Conflicts: selinux-policy < 3.13.1-92
Requires: libselinux >= 1.27.7
BuildRequires: libselinux-devel >= 1.27.7
Requires: audit-libs >= 1.0.8
BuildRequires: audit-libs >= 1.0.8
%endif
BuildRequires: xauth

%package clients
Summary: OpenSSH clients.
Requires: openssh = %{version}-%{release}
Group: Applications/Internet
Obsoletes: ssh-clients

%package server
Summary: The OpenSSH server daemon.
Group: System Environment/Daemons
Obsoletes: ssh-server
Requires: openssh = %{version}-%{release}, chkconfig >= 0.9
%if ! %{build6x}
Requires: /etc/pam.d/system-auth
%endif

%package askpass
Summary: A passphrase dialog for OpenSSH and X.
Group: Applications/Internet
Requires: openssh = %{version}-%{release}
Obsoletes: ssh-extras

%package askpass-gnome
Summary: A passphrase dialog for OpenSSH, X, and GNOME.
Group: Applications/Internet
Requires: openssh = %{version}-%{release}
Obsoletes: ssh-extras

%description
SSH (Secure SHell) is a program for logging into and executing
commands on a remote machine. SSH is intended to replace rlogin and
rsh, and to provide secure encrypted communications between two
untrusted hosts over an insecure network. X11 connections and
arbitrary TCP/IP ports can also be forwarded over the secure channel.

OpenSSH is OpenBSD's version of the last free version of SSH, bringing
it up to date in terms of security and features, as well as removing
all patented algorithms to separate libraries.

This package includes the core files necessary for both the OpenSSH
client and server. To make this package useful, you should also
install openssh-clients, openssh-server, or both.

%description clients
OpenSSH is a free version of SSH (Secure SHell), a program for logging
into and executing commands on a remote machine. This package includes
the clients necessary to make encrypted connections to SSH servers.
You'll also need to install the openssh package on OpenSSH clients.

%description server
OpenSSH is a free version of SSH (Secure SHell), a program for logging
into and executing commands on a remote machine. This package contains
the secure shell daemon (sshd). The sshd daemon allows SSH clients to
securely connect to your SSH server. You also need to have the openssh
package installed.

%description askpass
OpenSSH is a free version of SSH (Secure SHell), a program for logging
into and executing commands on a remote machine. This package contains
an X11 passphrase dialog for OpenSSH.

%description askpass-gnome
OpenSSH is a free version of SSH (Secure SHell), a program for logging
into and executing commands on a remote machine. This package contains
an X11 passphrase dialog for OpenSSH and the GNOME GUI desktop
environment.

%prep

%if ! %{no_x11_askpass}
%setup -q -a 1
%else
%setup -q
%endif

%build
%if %{rescue}
CFLAGS="$RPM_OPT_FLAGS -Os"; export CFLAGS
%endif

sed "/^#UsePAM no/i# WARNING: 'UsePAM no' is not supported in Red Hat Enterprise Linux and may cause several\n# problems." -i sshd_config
sed 's|^#UsePAM .*|UsePAM yes|g' -i sshd_config
sed '/^#PrintMotd .*/s|^#PrintMotd .*|\n# It is recommended to use pam_motd in /etc/pam.d/sshd instead of PrintMotd,\n# as it is more configurable and versatile than the built-in version.\nPrintMotd no\n|g' -i sshd_config
sed 's|^#SyslogFacility .*|SyslogFacility AUTHPRIV|' -i sshd_config
sed 's|^#PermitRootLogin .*|PermitRootLogin yes|' -i sshd_config
sed 's@^#HostKey /etc/ssh/ssh_host_@HostKey /etc/ssh/ssh_host_@g' -i sshd_config
sed '/^#Port 22/i# If you want to change the port on a SELinux system, you have to tell\
# SELinux about this change.\
# semanage port -a -t ssh_port_t -p tcp #PORTNUMBER\
#' -i sshd_config

sed 's|^Subsystem[ \t]*sftp|#&|g' -i sshd_config
sed '/^#Subsystem.*sftp/aSubsystem\tsftp\tinternal-sftp' -i sshd_config

%configure \
    --sysconfdir=%{_sysconfdir}/ssh \
    --libexecdir=%{_libexecdir}/openssh \
    --datadir=%{_datadir}/openssh \
    --with-default-path=/usr/local/bin:/bin:/usr/bin \
    --with-superuser-path=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin \
    --with-privsep-path=%{_var}/empty/sshd \
    --mandir=%{_mandir} \
    --with-mantype=man \
    --disable-strip \
    --with-ssl-engine \
    --with-ipaddr-display \
    --with-systemd \
    --with-pam \
%if %{WITH_SELINUX}
    --with-selinux --with-audit=linux \
    --with-sandbox=seccomp_filter \
%endif
%if %{libedit}
    --with-libedit
%else
    --without-libedit
%endif

%if %{static_libcrypto}
perl -pi -e "s|-lcrypto|%{_libdir}/libcrypto.a|g" Makefile
%endif

make

%if ! %{no_x11_askpass}
pushd x11-ssh-askpass-%{aversion}
%configure --libexecdir=%{_libexecdir}/openssh
xmkmf -a
make
popd
%endif

# Define a variable to toggle gnome1/gtk2 building.  This is necessary
# because RPM doesn't handle nested %if statements.
%if %{gtk2}
        gtk2=yes
%else
        gtk2=no
%endif

%if ! %{no_gnome_askpass}
pushd contrib
if [ $gtk2 = yes ] ; then
        make gnome-ssh-askpass2
        mv gnome-ssh-askpass2 gnome-ssh-askpass
else
        make gnome-ssh-askpass1
        mv gnome-ssh-askpass1 gnome-ssh-askpass
fi
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/ssh
mkdir -p -m 0755 $RPM_BUILD_ROOT%{_libexecdir}/openssh
mkdir -p -m 0755 $RPM_BUILD_ROOT%{_var}/empty/sshd

make install DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -d $RPM_BUILD_ROOT%{_unitdir}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/systemd/system/sshd.service.d
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -d $RPM_BUILD_ROOT%{_libexecdir}/openssh
# %if %{build6x}
# install -m 0644 contrib/redhat/sshd.pam.old $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/sshd
# %else
# install -m 0644 contrib/redhat/sshd.pam     $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/sshd
# %endif
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/sshd
sleep 1
printf '\x23\x25\x50\x41\x4D\x2D\x31\x2E\x30\x0A\x61\x75\x74\x68\x20\x20\x20\x20\x20\x20\x20\x73\x75\x62\x73\x74\x61\x63\x6B\x20\x20\x20\x20\x20\x70\x61\x73\x73\x77\x6F\x72\x64\x2D\x61\x75\x74\x68\x0A\x61\x75\x74\x68\x20\x20\x20\x20\x20\x20\x20\x69\x6E\x63\x6C\x75\x64\x65\x20\x20\x20\x20\x20\x20\x70\x6F\x73\x74\x6C\x6F\x67\x69\x6E\x0A\x61\x63\x63\x6F\x75\x6E\x74\x20\x20\x20\x20\x72\x65\x71\x75\x69\x72\x65\x64\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x73\x65\x70\x65\x72\x6D\x69\x74\x2E\x73\x6F\x0A\x61\x63\x63\x6F\x75\x6E\x74\x20\x20\x20\x20\x72\x65\x71\x75\x69\x72\x65\x64\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x6E\x6F\x6C\x6F\x67\x69\x6E\x2E\x73\x6F\x0A\x61\x63\x63\x6F\x75\x6E\x74\x20\x20\x20\x20\x69\x6E\x63\x6C\x75\x64\x65\x20\x20\x20\x20\x20\x20\x70\x61\x73\x73\x77\x6F\x72\x64\x2D\x61\x75\x74\x68\x0A\x70\x61\x73\x73\x77\x6F\x72\x64\x20\x20\x20\x69\x6E\x63\x6C\x75\x64\x65\x20\x20\x20\x20\x20\x20\x70\x61\x73\x73\x77\x6F\x72\x64\x2D\x61\x75\x74\x68\x0A\x23\x20\x70\x61\x6D\x5F\x73\x65\x6C\x69\x6E\x75\x78\x2E\x73\x6F\x20\x63\x6C\x6F\x73\x65\x20\x73\x68\x6F\x75\x6C\x64\x20\x62\x65\x20\x74\x68\x65\x20\x66\x69\x72\x73\x74\x20\x73\x65\x73\x73\x69\x6F\x6E\x20\x72\x75\x6C\x65\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x72\x65\x71\x75\x69\x72\x65\x64\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x73\x65\x6C\x69\x6E\x75\x78\x2E\x73\x6F\x20\x63\x6C\x6F\x73\x65\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x72\x65\x71\x75\x69\x72\x65\x64\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x6C\x6F\x67\x69\x6E\x75\x69\x64\x2E\x73\x6F\x0A\x23\x20\x70\x61\x6D\x5F\x73\x65\x6C\x69\x6E\x75\x78\x2E\x73\x6F\x20\x6F\x70\x65\x6E\x20\x73\x68\x6F\x75\x6C\x64\x20\x6F\x6E\x6C\x79\x20\x62\x65\x20\x66\x6F\x6C\x6C\x6F\x77\x65\x64\x20\x62\x79\x20\x73\x65\x73\x73\x69\x6F\x6E\x73\x20\x74\x6F\x20\x62\x65\x20\x65\x78\x65\x63\x75\x74\x65\x64\x20\x69\x6E\x20\x74\x68\x65\x20\x75\x73\x65\x72\x20\x63\x6F\x6E\x74\x65\x78\x74\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x72\x65\x71\x75\x69\x72\x65\x64\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x73\x65\x6C\x69\x6E\x75\x78\x2E\x73\x6F\x20\x6F\x70\x65\x6E\x20\x65\x6E\x76\x5F\x70\x61\x72\x61\x6D\x73\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x72\x65\x71\x75\x69\x72\x65\x64\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x6E\x61\x6D\x65\x73\x70\x61\x63\x65\x2E\x73\x6F\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x6F\x70\x74\x69\x6F\x6E\x61\x6C\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x6B\x65\x79\x69\x6E\x69\x74\x2E\x73\x6F\x20\x66\x6F\x72\x63\x65\x20\x72\x65\x76\x6F\x6B\x65\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x6F\x70\x74\x69\x6F\x6E\x61\x6C\x20\x20\x20\x20\x20\x70\x61\x6D\x5F\x6D\x6F\x74\x64\x2E\x73\x6F\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x69\x6E\x63\x6C\x75\x64\x65\x20\x20\x20\x20\x20\x20\x70\x61\x73\x73\x77\x6F\x72\x64\x2D\x61\x75\x74\x68\x0A\x73\x65\x73\x73\x69\x6F\x6E\x20\x20\x20\x20\x69\x6E\x63\x6C\x75\x64\x65\x20\x20\x20\x20\x20\x20\x70\x6F\x73\x74\x6C\x6F\x67\x69\x6E\x0A' | dd seek=$((0x0)) conv=notrunc bs=1 of=$RPM_BUILD_ROOT%{_sysconfdir}/pam.d/sshd
chmod 0644 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/sshd
install -m 0755 contrib/ssh-copy-id $RPM_BUILD_ROOT%{_bindir}/ssh-copy-id
install -m 0755 contrib/ssh-copy-id.1 $RPM_BUILD_ROOT%{_mandir}/man1/ssh-copy-id.1
ln -svf ssh $RPM_BUILD_ROOT%{_bindir}/slogin
ln -svf ssh.1 $RPM_BUILD_ROOT%{_mandir}/man1/slogin.1
touch -r $RPM_BUILD_ROOT%{_bindir}/scp $RPM_BUILD_ROOT%{_bindir}/ssh-copy-id
touch -r $RPM_BUILD_ROOT%{_mandir}/man1/scp.1 $RPM_BUILD_ROOT%{_mandir}/man1/ssh-copy-id.1
printf '\x23\x20\x43\x6F\x6E\x66\x69\x67\x75\x72\x61\x74\x69\x6F\x6E\x20\x66\x69\x6C\x65\x20\x66\x6F\x72\x20\x74\x68\x65\x20\x73\x73\x68\x64\x20\x73\x65\x72\x76\x69\x63\x65\x2E\x0A\x0A\x23\x20\x54\x68\x65\x20\x73\x65\x72\x76\x65\x72\x20\x6B\x65\x79\x73\x20\x61\x72\x65\x20\x61\x75\x74\x6F\x6D\x61\x74\x69\x63\x61\x6C\x6C\x79\x20\x67\x65\x6E\x65\x72\x61\x74\x65\x64\x20\x69\x66\x20\x74\x68\x65\x79\x20\x61\x72\x65\x20\x6D\x69\x73\x73\x69\x6E\x67\x2E\x0A\x23\x20\x54\x6F\x20\x63\x68\x61\x6E\x67\x65\x20\x74\x68\x65\x20\x61\x75\x74\x6F\x6D\x61\x74\x69\x63\x20\x63\x72\x65\x61\x74\x69\x6F\x6E\x20\x75\x6E\x63\x6F\x6D\x6D\x65\x6E\x74\x20\x61\x6E\x64\x20\x63\x68\x61\x6E\x67\x65\x20\x74\x68\x65\x20\x61\x70\x70\x72\x6F\x70\x72\x69\x61\x74\x65\x0A\x23\x20\x6C\x69\x6E\x65\x2E\x20\x41\x63\x63\x65\x70\x74\x65\x64\x20\x6B\x65\x79\x20\x74\x79\x70\x65\x73\x20\x61\x72\x65\x3A\x20\x44\x53\x41\x20\x52\x53\x41\x20\x45\x43\x44\x53\x41\x20\x45\x44\x32\x35\x35\x31\x39\x2E\x0A\x23\x20\x54\x68\x65\x20\x64\x65\x66\x61\x75\x6C\x74\x20\x69\x73\x20\x22\x52\x53\x41\x20\x45\x43\x44\x53\x41\x20\x45\x44\x32\x35\x35\x31\x39\x22\x0A\x0A\x23\x20\x41\x55\x54\x4F\x43\x52\x45\x41\x54\x45\x5F\x53\x45\x52\x56\x45\x52\x5F\x4B\x45\x59\x53\x3D\x22\x22\x0A\x23\x20\x41\x55\x54\x4F\x43\x52\x45\x41\x54\x45\x5F\x53\x45\x52\x56\x45\x52\x5F\x4B\x45\x59\x53\x3D\x22\x52\x53\x41\x20\x45\x43\x44\x53\x41\x20\x45\x44\x32\x35\x35\x31\x39\x22\x0A\x0A\x23\x20\x44\x6F\x20\x6E\x6F\x74\x20\x63\x68\x61\x6E\x67\x65\x20\x74\x68\x69\x73\x20\x6F\x70\x74\x69\x6F\x6E\x20\x75\x6E\x6C\x65\x73\x73\x20\x79\x6F\x75\x20\x68\x61\x76\x65\x20\x68\x61\x72\x64\x77\x61\x72\x65\x20\x72\x61\x6E\x64\x6F\x6D\x0A\x23\x20\x67\x65\x6E\x65\x72\x61\x74\x6F\x72\x20\x61\x6E\x64\x20\x79\x6F\x75\x20\x52\x45\x41\x4C\x4C\x59\x20\x6B\x6E\x6F\x77\x20\x77\x68\x61\x74\x20\x79\x6F\x75\x20\x61\x72\x65\x20\x64\x6F\x69\x6E\x67\x0A\x0A\x53\x53\x48\x5F\x55\x53\x45\x5F\x53\x54\x52\x4F\x4E\x47\x5F\x52\x4E\x47\x3D\x30\x0A\x23\x20\x53\x53\x48\x5F\x55\x53\x45\x5F\x53\x54\x52\x4F\x4E\x47\x5F\x52\x4E\x47\x3D\x31\x0A' | dd seek=$((0x0)) conv=notrunc bs=1 of=$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/sshd
chmod 640 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/sshd
touch -r $RPM_BUILD_ROOT%{_sbindir}/sshd $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/sshd
rm -fr $RPM_BUILD_ROOT%{_unitdir}/sshd.service
echo '[Unit]
Description=OpenSSH server daemon
Documentation=man:sshd(8) man:sshd_config(5)
After=network.target

[Service]
Type=notify
EnvironmentFile=/etc/sysconfig/sshd
ExecStart=/usr/sbin/sshd -D $OPTIONS
ExecStartPost=/bin/sleep 0.1
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartSec=42s

[Install]
WantedBy=multi-user.target' > $RPM_BUILD_ROOT%{_unitdir}/sshd.service
chmod 644 $RPM_BUILD_ROOT%{_unitdir}/sshd.service
# sed '/#SyslogFacility AUTH$/aSyslogFacility AUTHPRIV' -i $RPM_BUILD_ROOT%{_sysconfdir}/ssh/sshd_config
cp -pf $RPM_BUILD_ROOT%{_sysconfdir}/ssh/ssh_config $RPM_BUILD_ROOT%{_sysconfdir}/ssh/ssh_config.default
cp -pf $RPM_BUILD_ROOT%{_sysconfdir}/ssh/sshd_config $RPM_BUILD_ROOT%{_sysconfdir}/ssh/sshd_config.default
# sed 's@^#HostKey /etc/ssh/ssh_host_@HostKey /etc/ssh/ssh_host_@g' -i $RPM_BUILD_ROOT%{_sysconfdir}/ssh/sshd_config

%if ! %{no_x11_askpass}
install x11-ssh-askpass-%{aversion}/x11-ssh-askpass $RPM_BUILD_ROOT%{_libexecdir}/openssh/x11-ssh-askpass
ln -s x11-ssh-askpass $RPM_BUILD_ROOT%{_libexecdir}/openssh/ssh-askpass
%endif

%if ! %{no_gnome_askpass}
install contrib/gnome-ssh-askpass $RPM_BUILD_ROOT%{_libexecdir}/openssh/gnome-ssh-askpass
%endif

%if ! %{scard}
         rm -f $RPM_BUILD_ROOT/usr/share/openssh/Ssh.bin
%endif

%if ! %{no_gnome_askpass}
install -m 0755 -d $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/
install -m 0755 contrib/redhat/gnome-ssh-askpass.csh $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/
install -m 0755 contrib/redhat/gnome-ssh-askpass.sh $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/
%endif

perl -pi -e "s|$RPM_BUILD_ROOT||g" $RPM_BUILD_ROOT%{_mandir}/man*/*

############################################################################
# Generating hardening options
cd $RPM_BUILD_ROOT
rm -f etc/ssh/ssh-hardening-options.txt

echo "Ciphers $(./usr/bin/ssh -Q cipher | grep -iE '256.*gcm|gcm.*256|chacha' | paste -sd','),$(./usr/bin/ssh -Q cipher | grep -ivE 'gcm|chacha|cbc' | grep '256' | paste -sd',')" >> etc/ssh/ssh-hardening-options.txt

echo "MACs $(./usr/bin/ssh -Q mac | grep -i 'hmac-sha[23]' | grep -E '256|512' | grep '[0-9]$' | sort -r | paste -sd','),$(./usr/bin/ssh -Q mac | grep -i 'hmac-sha[23]' | grep -E '256|512' | grep '\@' | sort -r | paste -sd',')" >> etc/ssh/ssh-hardening-options.txt

echo "KexAlgorithms $(./usr/bin/ssh -Q kex | grep -iE '25519|448' | grep -iv '\@libssh' | sort -r | paste -sd','),$(./usr/bin/ssh -Q kex | grep -i 'ecdh-sha[23]-nistp5' | sort -r | paste -sd',')" >> etc/ssh/ssh-hardening-options.txt

echo "PubkeyAcceptedAlgorithms $(./usr/bin/ssh -Q PubkeyAcceptedAlgorithms | grep -iE 'ed25519|ed448|sha[23].*nistp521' | grep -v '\@' | paste -sd','),$(./usr/bin/ssh -Q PubkeyAcceptedAlgorithms | grep -iE 'ed25519|ed448|sha[23].*nistp521' | grep '\@' | paste -sd','),$(./usr/bin/ssh -Q PubkeyAcceptedAlgorithms | grep -i 'rsa-' | grep -i 'sha[23]-512' | paste -sd',')" >> etc/ssh/ssh-hardening-options.txt

echo "HostKeyAlgorithms $(./usr/bin/ssh -Q HostKeyAlgorithms | grep -iE 'ed25519|ed448|sha[23].*nistp521' | grep -v '\@' | paste -sd','),$(./usr/bin/ssh -Q HostKeyAlgorithms | grep -iE 'ed25519|ed448|sha[23].*nistp521' | grep '\@' | paste -sd','),$(./usr/bin/ssh -Q HostKeyAlgorithms | grep -i 'rsa-' | grep -i 'sha[23]-512' | paste -sd',')" >> etc/ssh/ssh-hardening-options.txt

echo "HostbasedAcceptedAlgorithms $(./usr/bin/ssh -Q HostbasedAcceptedAlgorithms | grep -iE 'ed25519|ed448|sha[23].*nistp521' | grep -v '\@' | paste -sd','),$(./usr/bin/ssh -Q HostbasedAcceptedAlgorithms | grep -iE 'ed25519|ed448|sha[23].*nistp521' | grep '\@' | paste -sd','),$(./usr/bin/ssh -Q HostbasedAcceptedAlgorithms | grep -i 'rsa-' | grep -i 'sha[23]-512' | paste -sd',')" >> etc/ssh/ssh-hardening-options.txt
############################################################################

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group ssh_keys >/dev/null || groupadd -r ssh_keys || : 

%pre server
getent group sshd >/dev/null || groupadd -g %{sshd_gid} -r sshd || : 
getent passwd sshd >/dev/null || \
  useradd -c "Privilege-separated SSH" -u %{sshd_uid} -g sshd \
  -s /sbin/nologin -r -d /var/empty/sshd sshd 2> /dev/null || : 

%post server
/bin/rm -f /etc/ssh/ssh_host_rsa_key
/bin/rm -f /etc/ssh/ssh_host_rsa_key.pub
/bin/rm -f /etc/ssh/ssh_host_dsa_key
/bin/rm -f /etc/ssh/ssh_host_dsa_key.pub
/bin/rm -f /etc/ssh/ssh_host_ecdsa_key
/bin/rm -f /etc/ssh/ssh_host_ecdsa_key.pub
/bin/rm -f /etc/ssh/ssh_host_ed25519_key
/bin/rm -f /etc/ssh/ssh_host_ed25519_key.pub
/bin/ssh-keygen -q -a 200 -t rsa -b 5120 -E sha512 -f /etc/ssh/ssh_host_rsa_key -N "" -C ""
/bin/ssh-keygen -q -a 200 -t dsa -E sha512 -f /etc/ssh/ssh_host_dsa_key -N "" -C ""
/bin/ssh-keygen -q -a 200 -t ecdsa -b 521 -E sha512 -f /etc/ssh/ssh_host_ecdsa_key -N "" -C ""
/bin/ssh-keygen -q -a 200 -t ed25519 -E sha512 -f /etc/ssh/ssh_host_ed25519_key -N "" -C ""
/bin/systemctl daemon-reload >/dev/null 2>&1 || : 
/bin/systemctl enable sshd.service >/dev/null 2>&1 || : 

%postun server
/bin/systemctl daemon-reload >/dev/null 2>&1 || : 

%preun server
if [ $1 -eq 0 ] ; then 
        # Package removal, not upgrade 
        /bin/systemctl --no-reload disable sshd.service sshd.socket >/dev/null 2>&1 || : 
        /bin/systemctl stop sshd.service sshd.socket >/dev/null 2>&1 || : 
fi

%files
%defattr(-,root,root)
%license LICENCE
%doc CREDITS ChangeLog INSTALL OVERVIEW README* PROTOCOL* TODO
%attr(0755,root,root) %dir %{_sysconfdir}/ssh
%attr(0600,root,root) %config %{_sysconfdir}/ssh/moduli
%attr(0644,root,root) %{_sysconfdir}/ssh/ssh-hardening-options.txt
%if ! %{rescue}
%attr(0755,root,root) %{_bindir}/ssh-keygen
%attr(0644,root,root) %{_mandir}/man1/ssh-keygen.1*
%attr(0755,root,root) %dir %{_libexecdir}/openssh
%attr(4711,root,root) %{_libexecdir}/openssh/ssh-keysign
%attr(0644,root,root) %{_mandir}/man8/ssh-keysign.8*
%endif
%if %{scard}
%attr(0755,root,root) %dir %{_datadir}/openssh
%attr(0644,root,root) %{_datadir}/openssh/Ssh.bin
%endif

%files clients
%defattr(-,root,root)
%{_bindir}/slogin
%{_mandir}/man1/slogin.1*
%attr(0755,root,root) %{_bindir}/ssh
%attr(0755,root,root) %{_bindir}/scp
%attr(0755,root,root) %{_bindir}/ssh-copy-id
%attr(0644,root,root) %{_mandir}/man1/ssh.1*
%attr(0644,root,root) %{_mandir}/man1/scp.1*
%attr(0644,root,root) %{_mandir}/man1/ssh-copy-id.1*
%attr(0644,root,root) %{_mandir}/man5/ssh_config.5*
%attr(0644,root,root) %config %{_sysconfdir}/ssh/ssh_config
%attr(0644,root,root) %{_sysconfdir}/ssh/ssh_config.default
%if ! %{rescue}
%attr(2755,root,nobody) %{_bindir}/ssh-agent
%attr(0755,root,root) %{_bindir}/ssh-add
%attr(0755,root,root) %{_bindir}/ssh-keyscan
%attr(0755,root,root) %{_bindir}/sftp
%attr(0755,root,root) %{_libexecdir}/openssh/ssh-pkcs11-helper
%attr(0755,root,root) %{_libexecdir}/openssh/ssh-sk-helper
%attr(0644,root,root) %{_mandir}/man8/ssh-pkcs11-helper.8*
%attr(0644,root,root) %{_mandir}/man8/ssh-sk-helper.8*
%attr(0644,root,root) %{_mandir}/man1/ssh-agent.1*
%attr(0644,root,root) %{_mandir}/man1/ssh-add.1*
%attr(0644,root,root) %{_mandir}/man1/ssh-keyscan.1*
%attr(0644,root,root) %{_mandir}/man1/sftp.1*
%endif

%if ! %{rescue}
%files server
%defattr(-,root,root)
%dir %attr(0711,root,root) %{_var}/empty/sshd
%attr(0755,root,root) %{_sbindir}/sshd
%attr(0755,root,root) %{_libexecdir}/openssh/sftp-server
%attr(0644,root,root) %{_mandir}/man8/sshd.8*
%attr(0644,root,root) %{_mandir}/man5/moduli.5*
%attr(0644,root,root) %{_mandir}/man5/sshd_config.5*
%attr(0644,root,root) %{_mandir}/man8/sftp-server.8*
%attr(0755,root,root) %dir %{_sysconfdir}/ssh
%attr(0600,root,root) %config %{_sysconfdir}/ssh/sshd_config
%attr(0600,root,root) %{_sysconfdir}/ssh/sshd_config.default
%attr(0644,root,root) %config %{_sysconfdir}/pam.d/sshd
%attr(0640,root,root) %{_sysconfdir}/sysconfig/sshd
%attr(0644,root,root) %{_unitdir}/sshd.service
%attr(0755,root,root) %dir %{_sysconfdir}/systemd/system/sshd.service.d
%endif

%if ! %{no_x11_askpass}
%files askpass
%defattr(-,root,root)
%doc x11-ssh-askpass-%{aversion}/README
%doc x11-ssh-askpass-%{aversion}/ChangeLog
%doc x11-ssh-askpass-%{aversion}/SshAskpass*.ad
%{_libexecdir}/openssh/ssh-askpass
%attr(0755,root,root) %{_libexecdir}/openssh/x11-ssh-askpass
%endif

%if ! %{no_gnome_askpass}
%files askpass-gnome
%defattr(-,root,root)
%attr(0755,root,root) %config %{_sysconfdir}/profile.d/gnome-ssh-askpass.*
%attr(0755,root,root) %{_libexecdir}/openssh/gnome-ssh-askpass
%endif


