%define rname phpMyAdmin

%if %mandriva_branch == Cooker
# Cooker
%define release %mkrel 1
%else
# Old distros
%define subrel 1
%define release %mkrel 0
%endif

Summary:	Handles the administration of MySQL over the web
Name:		phpmyadmin
Version:	3.4.5
Release:	%release
License:	GPLv2
Group:		System/Servers
URL:		http://www.phpmyadmin.net/
Source0:	http://prdownloads.sourceforge.net/phpmyadmin/%{rname}-%{version}-all-languages.tar.gz
Source1:	phpmyadmin-16x16.png
Source2:	phpmyadmin-32x32.png
Source3:	phpmyadmin-48x48.png
Requires:	apache-mod_php
Requires:	php-mysql
Requires:	php-mbstring
Requires:	php-mcrypt
%if %mdkversion < 201010
Requires(post): rpm-helper
Requires(postun): rpm-helper
%endif
BuildArch:	noarch
Obsoletes:	phpMyAdmin
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
phpMyAdmin is intended to handle the administration of MySQL over the web.
Currently it can : create and drop databases, create, copy, drop and alter
tables, delete, edit and add fields, execute any SQL-statement, even
batch-queries, manage keys on fields, load text files into tables, create and
read dumps of tables, export data to CSV value, administer multiple servers
and single databases.

%prep
%setup -q -n %{rname}-%{version}-all-languages

%build

%install
rm -rf %{buildroot}

export DONT_RELINK=1

install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_datadir}/%{name}

cp -aRf * %{buildroot}%{_datadir}/%{name}/

# cleanup
pushd %{buildroot}%{_datadir}/%{name}
    rm -f CREDITS ChangeLog Documentation.txt INSTALL LICENSE README 
    rm -f README.VENDOR RELEASE-DATE-* TODO
    rm -rf scripts
    rm -rf contrib
    rm -f lang/*.sh libraries/transformations/*.sh
    find -name "\.htaccess" | xargs rm -f
popd

# fix config file location
mv %{buildroot}%{_datadir}/%{name}/config.sample.inc.php \
    %{buildroot}%{_sysconfdir}/%{name}/config.php

pushd  %{buildroot}%{_datadir}/%{name}
    ln -s %{_sysconfdir}/%{name}/config.php config.inc.php
popd
chmod 640 %{buildroot}%{_sysconfdir}/%{name}/config.php

cat > README.urpmi << EOF
The actual configuration file is /etc/phpmyadmin/config.php.
The config.default.inc.php file contains default values, and is not supposed to 
be modified.
EOF

install -d -m 755 %{buildroot}%{webappconfdir}
cat > %{buildroot}%{webappconfdir}/%{name}.conf << EOF
Alias /%{name} %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{webappconfdir}/%{name}.conf"

    php_flag session.auto_start 0
</Directory>

<Directory %{_datadir}/%{name}/libraries>
    Order deny,allow
    Deny from all
</Directory>
EOF

# Mandriva Icons
install -d %{buildroot}%{_iconsdir}
install -d %{buildroot}%{_miconsdir}
install -d %{buildroot}%{_liconsdir}

install -m0644 %{SOURCE1} %{buildroot}%{_miconsdir}/%{name}.png
install -m0644 %{SOURCE2} %{buildroot}%{_iconsdir}/%{name}.png
install -m0644 %{SOURCE3} %{buildroot}%{_liconsdir}/%{name}.png

# install menu entry.
# XDG menu
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=phpMyAdmin
Comment=%{summary}
Exec=%{_bindir}/www-browser http://localhost/%{name}/
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Databases;
EOF

# fix borked permissions
find %{buildroot}%{_datadir}/%{name} -type d -exec chmod 755 {} \;
find %{buildroot}%{_datadir}/%{name} -type f -exec chmod 644 {} \;

%pretrans
# fix configuration file name change
if [ -f %{_sysconfdir}/phpmyadmin/config.default.php ]; then
    mv %{_sysconfdir}/phpmyadmin/config.default.php \
        %{_sysconfdir}/phpmyadmin/config.php
fi
if [ -L /var/www/phpmyadmin/libraries/config.default.php ]; then
    rm -f /var/www/phpmyadmin/libraries/config.default.php
fi
if [ -L %{_datadir}/phpmyadmin/libraries/config.default.php ]; then
    rm -f %{_datadir}/phpmyadmin/libraries/config.default.php
fi

%post
# generate random secret
secret=%_get_password 46

# blowfish secret
perl -pi \
    -e "s|\\\$cfg\\['blowfish_secret'\\] = ''|\\\$cfg\\['blowfish_secret'\\] = '$secret'|" \
    %{_sysconfdir}/%{name}/config.php

%if %mdkversion < 201010
%_post_webapp
%endif
%if %mdkversion < 200900
%update_menus
%endif

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif
%if %mdkversion < 200900
%clean_menus
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CREDITS ChangeLog Documentation.txt INSTALL LICENSE README RELEASE-DATE-* TODO scripts README.urpmi
%config(noreplace) %{webappconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(-,root,apache) %config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_datadir}/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
