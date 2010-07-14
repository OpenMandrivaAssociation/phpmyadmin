%define rname phpMyAdmin

%define betaver 0
%define rel 1 

%if %betaver
%define tarballver %version-%betaver
%define release %mkrel -c %betaver %rel
%else
%define tarballver %version
%define release %mkrel %rel
%endif

Summary:        Handles the administration of MySQL over the web
Name:           phpmyadmin
Version:        3.3.4
Release:        %release
License:        GPLv2
Group:          System/Servers
URL:            http://www.phpmyadmin.net/
Source0:        http://prdownloads.sourceforge.net/phpmyadmin/%{rname}-%{tarballver}-all-languages.tar.bz2
Source10:       http://prdownloads.sourceforge.net/phpmyadmin/aqua-2.2a.tar.bz2
Source11:       http://prdownloads.sourceforge.net/phpmyadmin/arctic_ocean-3.3.tar.bz2
Source12:       http://prdownloads.sourceforge.net/phpmyadmin/paradice-3.0a.tar.bz2
Source13:       http://prdownloads.sourceforge.net/phpmyadmin/xp_basic-2.1.tar.bz2
Source14:       http://prdownloads.sourceforge.net/phpmyadmin/crimson_gray-3.1-3.2.tar.bz2
Source15:       http://prdownloads.sourceforge.net/phpmyadmin/hillside-3.0.tar.bz2
Source16:       http://prdownloads.sourceforge.net/phpmyadmin/smooth_yellow-3.3.tar.bz2
Requires:       apache-mod_php
Requires:       php-mysql
Requires:       php-mbstring
Requires:       php-mcrypt
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
BuildArch:      noarch
BuildRequires:  ImageMagick
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
phpMyAdmin is intended to handle the administration of MySQL over
the web. Currently it can : create and drop databases, create,
copy, drop and alter tables, delete, edit and add fields, execute
any SQL-statement, even batch-queries, manage keys on fields, load
text files into tables, create and read dumps of tables, export
data to CSV value, administer multiple servers and single
databases.

%prep
%setup -q -n %{rname}-%{tarballver}-all-languages

pushd themes
for i in %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13}; do
    tar -jxf $i
done
popd

%build

%install
rm -rf %{buildroot}

export DONT_RELINK=1
 
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}/var/www/%{name}

cp -aRf * %{buildroot}/var/www/%{name}/

# cleanup
pushd %{buildroot}/var/www/%{name}
    rm -f CREDITS ChangeLog Documentation.txt INSTALL LICENSE README 
    rm -f README.VENDOR RELEASE-DATE-* TODO
    rm -rf scripts
    rm -rf contrib
    rm -f lang/*.sh libraries/transformations/*.sh
    find -name "\.htaccess" | xargs rm -f
popd

# fix config file location
mv %{buildroot}/var/www/%{name}/config.sample.inc.php \
    %{buildroot}%{_sysconfdir}/%{name}/config.php
pushd  %{buildroot}/var/www/%{name}
ln -s ../../..%{_sysconfdir}/%{name}/config.php config.inc.php
popd
chmod 640 %{buildroot}%{_sysconfdir}/%{name}/config.php

cat > README.urpmi << EOF
The actual configuration file is /etc/phpmyadmin/config.php.
The config.default.inc.php file contains default values, and is not supposed to 
be modified.
EOF

install -d -m 755 %{buildroot}%{webappconfdir}
cat > %{buildroot}%{webappconfdir}/%{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory /var/www/%{name}>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{webappconfdir}/%{name}.conf"

    php_flag session.auto_start 0
</Directory>

<Directory /var/www/%{name}/libraries>
    Order deny,allow
    Deny from all
</Directory>
EOF

# Mandriva Icons
install -d %{buildroot}%{_iconsdir}
install -d %{buildroot}%{_miconsdir}
install -d %{buildroot}%{_liconsdir}

convert themes/original/img/logo_right.png -resize 16x16  %{buildroot}%{_miconsdir}/%{name}.png
convert themes/original/img/logo_right.png -resize 32x32  %{buildroot}%{_iconsdir}/%{name}.png
convert themes/original/img/logo_right.png -resize 48x48  %{buildroot}%{_liconsdir}/%{name}.png

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

%pretrans 
# fix configuration file name change
if [ -f %{_sysconfdir}/phpmyadmin/config.default.php ]; then
    mv %{_sysconfdir}/phpmyadmin/config.default.php \
        %{_sysconfdir}/phpmyadmin/config.php
fi
if [ -L /var/www/phpmyadmin/libraries/config.default.php ]; then
    rm -f /var/www/phpmyadmin/libraries/config.default.php
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
/var/www/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
