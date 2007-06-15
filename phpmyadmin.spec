%define rname phpMyAdmin

Summary:        Handles the administration of MySQL over the web
Name:           phpmyadmin
Version:        2.10.2
Release:        %mkrel 1
License:        GPL
Group:          System/Servers
URL:            http://www.phpmyadmin.net/
Source0:        http://prdownloads.sourceforge.net/phpmyadmin/%{rname}-%{version}-all-languages.tar.bz2
Source10:       http://prdownloads.sourceforge.net/phpmyadmin/aqua-2.2a.tar.bz2
Source11:       http://prdownloads.sourceforge.net/phpmyadmin/arctic_ocean-2.2a.tar.bz2
Source12:       http://prdownloads.sourceforge.net/phpmyadmin/paradice-2.2a.tar.bz2
Source13:       http://prdownloads.sourceforge.net/phpmyadmin/xp_basic-2.1.tar.bz2
Patch0:         phpMyAdmin-use-cookie-in-config.diff
Patch1:         phpMyAdmin-2.8.2.1-bug23847.diff
Patch2:         phpMyAdmin-bug22020.diff
Requires(pre):  apache-mod_php php-mysql php-mbstring php-mcrypt
Requires:       apache-mod_php php-mysql php-mbstring php-mcrypt
Requires(post): rpm-helper
Requires(postun): rpm-helper
BuildArch:      noarch
BuildRequires:  ImageMagick
BuildRequires:  apache-base >= 2.0.54
BuildRoot:      %{_tmppath}/%{name}-buildroot

Obsoletes: phpMyAdmin
Conflicts: phpMyAdmin

# Macro for generating an environment variable (%1) with %2 random characters
%define randstr() %1=`perl -e 'for ($i = 0, $bit = "!", $key = ""; $i < %2; $i++) {while ($bit !~ /^[0-9A-Za-z]$/) { $bit = chr(rand(90) + 32); } $key .= $bit; $bit = "!"; } print "$key";'`

%description
phpMyAdmin is intended to handle the administration of MySQL over
the web. Currently it can : create and drop databases, create,
copy, drop and alter tables, delete, edit and add fields, execute
any SQL-statement, even batch-queries, manage keys on fields, load
text files into tables, create and read dumps of tables, export
data to CSV value, administer multiple servers and single
databases.

%prep
%setup -q -n %{rname}-%{version}-all-languages
%patch0 -p0
%patch1 -p1
%patch2 -p1

pushd themes
for i in %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13}; do
    tar -jxf $i
done
popd

# strip away annoying ^M
find -type f | grep -v "\.gif" | grep -v "\.png" | grep -v "\.jpg" | grep -v "\.z" | xargs %{__perl} -pi -e 's/\r$//g'

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
    rm -f CREDITS ChangeLog Documentation.txt INSTALL LICENSE README RELEASE-DATE-* TODO
    rm -rf scripts
    rm -f lang/*.sh libraries/transformations/*.sh
    find -name "\.htaccess" | xargs rm -f
popd

# fix config file location
mv %{buildroot}/var/www/%{name}/libraries/config.default.php %{buildroot}%{_sysconfdir}/%{name}/
ln -s %{_sysconfdir}/%{name}/config.default.php %{buildroot}/var/www/%{name}/libraries/config.default.php

cat > README.urpmi << EOF
The config file name has changed name from config.inc.php to 
config.default.php. From 2.8.0 the file moved into libraries/

Now the file is put in /etc/phpMyAdmin/config.default.php and softlinked
to /var/www/%{name}/libraries/config.default.php
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
install -d %{buildroot}%{_menudir}
cat > %{buildroot}%{_menudir}/%{name} << EOF
?package(%{name}): \
needs=X11 \
section="More Applications/Databases" \
title="phpMyAdmin" \
longtitle="Web administration GUI for MySQL" \
command="%{_bindir}/www-browser http://localhost/%{name}/" \
icon="%{name}.png" \
xdg=true
EOF

# XDG menu
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=phpMyAdmin
Comment=%{summary}
Exec="%{_bindir}/www-browser http://localhost/%{name}/"
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Databases;
EOF

%post

%randstr BLOWFISH 8

BLOWFISH=`echo -n $BLOWFISH | md5sum | awk '{print $1}'`
perl -pi -e "s|_BLOWFISH_SECRET_|$BLOWFISH|g" %{_sysconfdir}/%{name}/config.default.php

%_post_webapp
%update_menus

%postun
%_postun_webapp
%clean_menus

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%doc CREDITS ChangeLog Documentation.txt INSTALL LICENSE README RELEASE-DATE-* TODO scripts README.urpmi 
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%dir %attr(0755,root,root) %{_sysconfdir}/%{name}
%attr(0640,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/config.default.php
/var/www/%{name}
%{_menudir}/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
