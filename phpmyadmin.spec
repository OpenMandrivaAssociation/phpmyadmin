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
Version:        3.2.2
Release:        %release
License:        GPLv2
Group:          System/Servers
URL:            http://www.phpmyadmin.net/
Source0:        http://prdownloads.sourceforge.net/phpmyadmin/%{rname}-%{tarballver}-all-languages.tar.bz2
Source10:       http://prdownloads.sourceforge.net/phpmyadmin/aqua-2.2a.tar.bz2
Source11:       http://prdownloads.sourceforge.net/phpmyadmin/arctic_ocean-2.11a.tar.bz2
Source12:       http://prdownloads.sourceforge.net/phpmyadmin/paradice-2.10a.tar.bz2
Source13:       http://prdownloads.sourceforge.net/phpmyadmin/xp_basic-2.1.tar.bz2
Patch2:         phpMyAdmin-bug22020.diff
Requires(pre):  apache-mod_php php-mysql php-mbstring php-mcrypt
Requires:       apache-mod_php php-mysql php-mbstring php-mcrypt
Requires(post): rpm-helper
Requires(postun): rpm-helper
BuildArch:      noarch
BuildRequires:  ImageMagick
BuildRequires:  apache-base >= 2.0.54
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

Obsoletes: phpMyAdmin
Conflicts: phpMyAdmin

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
%patch2 -p1

pushd themes
for i in %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13}; do
    tar -jxf $i
done
popd

%build

%install
rm -rf %{buildroot}

export DONT_RELINK=1
 
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
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

cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf << EOF

Alias /%{name} /var/www/%{name}

<IfModule mod_php4.c>
    php_flag session.auto_start 0
</IfModule>

<IfModule mod_php5.c>
    php_flag session.auto_start 0
</IfModule>

<Directory /var/www/%{name}>
    Allow from All
</Directory>

<Directory /var/www/%{name}/libraries>
    Order Deny,Allow
    Deny from All
    Allow from None
</Directory>

# Uncomment the following lines to force a redirect to a working 
# SSL aware apache server. This serves as an example.
# 
#<IfModule mod_ssl.c>
#    <LocationMatch /%{name}>
#        Options FollowSymLinks
#        RewriteEngine on
#        RewriteCond %{SERVER_PORT} !^443$
#        RewriteRule ^.*$ https://%{SERVER_NAME}%{REQUEST_URI} [L,R]
#    </LocationMatch>
#</IfModule>

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

%_post_webapp
%if %mdkversion < 200900
%update_menus
%endif

%postun
%_postun_webapp
%if %mdkversion < 200900
%clean_menus
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CREDITS ChangeLog Documentation.txt INSTALL LICENSE README RELEASE-DATE-* TODO scripts README.urpmi 
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(-,root,apache) %config(noreplace) %{_sysconfdir}/%{name}/config.php
/var/www/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
