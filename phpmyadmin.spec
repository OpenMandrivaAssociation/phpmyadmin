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
Version:	3.5.2
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

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog Documentation.txt LICENSE README RELEASE-DATE-* examples README.urpmi
%config(noreplace) %{webappconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(-,root,apache) %config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_datadir}/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop


%changelog
* Mon Jul 09 2012 Oden Eriksson <oeriksson@mandriva.com> 3.5.2-1mdv2012.0
+ Revision: 808558
- 3.5.2

* Mon May 07 2012 Oden Eriksson <oeriksson@mandriva.com> 3.5.1-1
+ Revision: 797257
- 3.5.1

* Sun Apr 08 2012 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-1
+ Revision: 789843
- 3.5.0

* Thu Mar 29 2012 Oden Eriksson <oeriksson@mandriva.com> 3.4.10.2-1
+ Revision: 788220
- 3.4.10.2

* Wed Feb 15 2012 Oden Eriksson <oeriksson@mandriva.com> 3.4.10-1
+ Revision: 774360
- 3.4.10

* Thu Jan 19 2012 Oden Eriksson <oeriksson@mandriva.com> 3.4.9-1
+ Revision: 762390
- sync with MDVSA-2011:198

* Fri Dec 02 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.8-1
+ Revision: 737209
- 3.4.8

* Sat Nov 12 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.7.1-1
+ Revision: 730239
- 3.4.7.1

* Fri Oct 21 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.6-1
+ Revision: 705578
- 3.4.6

* Wed Sep 14 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.5-1
+ Revision: 699796
- 3.4.5

* Thu Aug 25 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.4-1
+ Revision: 696552
- 3.4.4

* Sun Jul 24 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.3.2-1
+ Revision: 691379
- 3.4.3.2
- 3.4.3.1

* Wed Jun 08 2011 Funda Wang <fwang@mandriva.org> 3.4.2-1
+ Revision: 683135
- update to new version 3.4.2

* Sat May 21 2011 Funda Wang <fwang@mandriva.org> 3.4.1-1
+ Revision: 676513
- update to new version 3.4.1

* Thu May 12 2011 Oden Eriksson <oeriksson@mandriva.com> 3.4.0-1
+ Revision: 673761
- 3.4.0

* Sun Mar 20 2011 Funda Wang <fwang@mandriva.org> 3.3.10-1
+ Revision: 647064
- update to new version 3.3.10

* Sat Mar 12 2011 Funda Wang <fwang@mandriva.org> 3.3.9.2-3
+ Revision: 643942
- rebuild

* Sun Feb 20 2011 Oden Eriksson <oeriksson@mandriva.com> 3.3.9.2-2
+ Revision: 638855
- added backporting magic
- cleanups
- drop the themes, old cruft
- provide the formatted icons
- relocate from /var/www to /usr/share

* Mon Feb 14 2011 Oden Eriksson <oeriksson@mandriva.com> 3.3.9.2-1
+ Revision: 637688
- 3.3.9.2

* Wed Feb 09 2011 Funda Wang <fwang@mandriva.org> 3.3.9.1-1
+ Revision: 636955
- update to new version 3.3.9.1

* Tue Jan 04 2011 Funda Wang <fwang@mandriva.org> 3.3.9-1mdv2011.0
+ Revision: 628503
- update to new version 3.3.9

* Tue Nov 30 2010 Funda Wang <fwang@mandriva.org> 3.3.8.1-1mdv2011.0
+ Revision: 603246
- update to new version 3.3.8.1

* Tue Nov 23 2010 Oden Eriksson <oeriksson@mandriva.com> 3.3.8-2mdv2011.0
+ Revision: 600170
- make it actually work, duh!

* Tue Oct 26 2010 Funda Wang <fwang@mandriva.org> 3.3.8-1mdv2011.0
+ Revision: 589408
- update to new version 3.3.8

* Wed Sep 08 2010 Funda Wang <fwang@mandriva.org> 3.3.7-1mdv2011.0
+ Revision: 576722
- update to new version 3.3.7

* Sun Aug 29 2010 Funda Wang <fwang@mandriva.org> 3.3.6-1mdv2011.0
+ Revision: 574036
- update to new version 3.3.6

* Fri Aug 20 2010 Funda Wang <fwang@mandriva.org> 3.3.5.1-1mdv2011.0
+ Revision: 571511
- update to new version 3.3.5.1

* Tue Jul 27 2010 Funda Wang <fwang@mandriva.org> 3.3.5-1mdv2011.0
+ Revision: 560899
- update to new version 3.3.5

* Wed Jul 14 2010 Juan Luis Baptiste <juancho@mandriva.org> 3.3.4-1mdv2011.0
+ Revision: 553338
- Updated to 3.3.4.

* Wed Jun 09 2010 Ahmad Samir <ahmadsamir@mandriva.org> 3.3.3-3mdv2011.0
+ Revision: 547338
- revert last commit, such changes should be discussed with the maintainer first
  and should never happen so late in the release cycle

* Wed Jun 09 2010 Raphaël Gertz <rapsys@mandriva.org> 3.3.3-3mdv2010.1
+ Revision: 547298
- Replace ccp noorphans by alloworphans

* Wed Jun 09 2010 Raphaël Gertz <rapsys@mandriva.org> 3.3.3-2mdv2010.1
+ Revision: 547297
- Inscrease release
- Add merge of config file for smooth upgrade

  + Juan Luis Baptiste <juancho@mandriva.org>
    - Updated to 3.3.3."
    - Updated themes: aqua, artic and paradise and added crimson_gray, hillslide and smooth_yellow.

* Tue May 25 2010 Juan Luis Baptiste <juancho@mandriva.org> 3.3.2-2mdv2010.1
+ Revision: 545836
- Added patch to fix bug 59446: phpmyadmin shows utf8_bin fields in hex format.
- Fixed bug #58925, 600 permissions of theme directory.

* Mon Apr 19 2010 Funda Wang <fwang@mandriva.org> 3.3.2-1mdv2010.1
+ Revision: 536687
- update to new version 3.3.2

* Tue Mar 16 2010 Funda Wang <fwang@mandriva.org> 3.3.1-1mdv2010.1
+ Revision: 522548
- update to new version 3.3.1

* Mon Mar 08 2010 Funda Wang <fwang@mandriva.org> 3.3.0-1mdv2010.1
+ Revision: 515959
- update to new version 3.3.0

* Sun Feb 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.5-5mdv2010.1
+ Revision: 501777
- oops, fix typo in apache configuration
- switch default access policy to 'open to localhost only', as it allows to modify server state

* Sun Feb 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.5-3mdv2010.1
+ Revision: 501772
- simplify apache configuration, as php4 is dead

* Sun Feb 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.5-2mdv2010.1
+ Revision: 501756
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Mon Jan 11 2010 Funda Wang <fwang@mandriva.org> 3.2.5-1mdv2010.1
+ Revision: 489621
- new version 3.2.5

  + Buchan Milne <bgmilne@mandriva.org>
    - Suggest php-bz2 and apache-mod_ssl (bug #56870)

* Thu Dec 03 2009 Funda Wang <fwang@mandriva.org> 3.2.4-1mdv2010.1
+ Revision: 472781
- new version 3.2.4

* Fri Nov 06 2009 Frederik Himpe <fhimpe@mandriva.org> 3.2.3-1mdv2010.1
+ Revision: 461952
- update to new version 3.2.3

* Tue Oct 13 2009 Oden Eriksson <oeriksson@mandriva.com> 3.2.2.1-1mdv2010.0
+ Revision: 457007
- 3.2.2.1 (This is a security release, fixing some XSS and SQL injection problems.)

* Sun Sep 13 2009 Frederik Himpe <fhimpe@mandriva.org> 3.2.2-1mdv2010.0
+ Revision: 438699
- update to new version 3.2.2

* Mon Aug 10 2009 Frederik Himpe <fhimpe@mandriva.org> 3.2.1-1mdv2010.0
+ Revision: 414366
- update to new version 3.2.1

* Tue Jun 30 2009 Frederik Himpe <fhimpe@mandriva.org> 3.2.0.1-1mdv2010.0
+ Revision: 391088
- update to new version 3.2.0.1

* Mon Jun 15 2009 Frederik Himpe <fhimpe@mandriva.org> 3.2.0-1mdv2010.0
+ Revision: 386104
- update to new version 3.2.0

* Fri May 15 2009 Frederik Himpe <fhimpe@mandriva.org> 3.1.5-1mdv2010.0
+ Revision: 376271
- update to new version 3.1.5

* Sat May 02 2009 Frederik Himpe <fhimpe@mandriva.org> 3.1.4-1mdv2010.0
+ Revision: 370738
- update to new version 3.1.4

* Wed Apr 15 2009 Oden Eriksson <oeriksson@mandriva.com> 3.1.3.2-1mdv2009.1
+ Revision: 367358
- 3.1.3.2 (security fixes)

* Wed Mar 25 2009 Frederik Himpe <fhimpe@mandriva.org> 3.1.3.1-1mdv2009.1
+ Revision: 361175
- update to new version 3.1.3.1

* Thu Mar 05 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.3-2mdv2009.1
+ Revision: 349001
- handle upgrade nicely
- fix config file substitution after install
- cleanup: apache only need read access on configuration file, not write
- no need for a patch to substitute a config file
- use standard rpm-helper macros to generate blowfish secret
- don't move the default configuration file, it is not supposed to be modified, but move the actuel configuration file instead
- more docroot cleanup
- don't duplicate spec-help job

* Tue Mar 03 2009 Oden Eriksson <oeriksson@mandriva.com> 3.1.3-1mdv2009.1
+ Revision: 348169
- 3.1.3

* Tue Jan 20 2009 Funda Wang <fwang@mandriva.org> 3.1.2-1mdv2009.1
+ Revision: 331514
- rediff css patch
- 3.1.2

* Wed Dec 10 2008 Funda Wang <fwang@mandriva.org> 3.1.1-1mdv2009.1
+ Revision: 312383
- update to new version 3.1.1

* Sat Nov 29 2008 Funda Wang <fwang@mandriva.org> 3.1.0-1mdv2009.1
+ Revision: 307960
- 3.1.0 final

* Wed Nov 19 2008 Funda Wang <fwang@mandriva.org> 3.1.0-0.rc1.1mdv2009.1
+ Revision: 304372
- New version 3.1.0 rc1
- rediff cookie patch

* Fri Oct 31 2008 Frederik Himpe <fhimpe@mandriva.org> 3.0.1.1-1mdv2009.1
+ Revision: 299008
- update to new version 3.0.1.1

* Fri Oct 24 2008 Funda Wang <fwang@mandriva.org> 3.0.1-1mdv2009.1
+ Revision: 296907
- new version 3.0.1 final

* Sun Oct 19 2008 Funda Wang <fwang@mandriva.org> 3.0.1-0.rc1.1mdv2009.1
+ Revision: 295281
- 3.0.1 rc1

* Sun Sep 28 2008 Funda Wang <fwang@mandriva.org> 3.0.0-1mdv2009.0
+ Revision: 288968
- New version 3.0.0 final

* Tue Sep 16 2008 Funda Wang <fwang@mandriva.org> 3.0.0-0.rc2.1mdv2009.0
+ Revision: 285104
- 3.0 rc2

* Sat Sep 13 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0.0-0.rc1.2mdv2009.0
+ Revision: 284499
- fix #35792 (Wrong config file location mentioned in urpmi readme file)

* Mon Sep 08 2008 Funda Wang <fwang@mandriva.org> 3.0.0-0.rc1.1mdv2009.0
+ Revision: 282440
- 3.0.0 rc1

* Sat Aug 23 2008 Funda Wang <fwang@mandriva.org> 3.0.0-0.beta.1mdv2009.0
+ Revision: 275351
- New version 3.0.0 beta

* Tue Jul 29 2008 Funda Wang <fwang@mandriva.org> 2.11.8.1-1mdv2009.0
+ Revision: 252408
- New version 2.11.8.1
- clearify the license

* Mon Jul 28 2008 Oden Eriksson <oeriksson@mandriva.com> 2.11.8-1mdv2009.0
+ Revision: 251707
- 2.11.8

* Wed Jul 16 2008 Funda Wang <fwang@mandriva.org> 2.11.7.1-1mdv2009.0
+ Revision: 236237
- update to new version 2.11.7.1

* Tue Jun 24 2008 Funda Wang <fwang@mandriva.org> 2.11.7-1mdv2009.0
+ Revision: 228492
- New version 2.11.7 final

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Wed Jun 11 2008 Funda Wang <fwang@mandriva.org> 2.11.7-0.rc1.1mdv2009.0
+ Revision: 217837
- New version 2.11.7 rc1

* Wed Apr 30 2008 Funda Wang <fwang@mandriva.org> 2.11.6-1mdv2009.0
+ Revision: 199365
- update to new version 2.11.6

* Fri Apr 25 2008 Funda Wang <fwang@mandriva.org> 2.11.5.2-1mdv2009.0
+ Revision: 197369
- update to new version 2.11.5.2

* Wed Apr 16 2008 Funda Wang <fwang@mandriva.org> 2.11.5.1-1mdv2009.0
+ Revision: 194528
- update to new version 2.11.5.1

* Sun Mar 02 2008 Funda Wang <fwang@mandriva.org> 2.11.5-1mdv2008.1
+ Revision: 177599
- update to new version 2.11.5

* Sat Jan 12 2008 Funda Wang <fwang@mandriva.org> 2.11.4-1mdv2008.1
+ Revision: 149733
- update to new version 2.11.4

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 09 2007 Funda Wang <fwang@mandriva.org> 2.11.3-1mdv2008.1
+ Revision: 116630
- update to new version 2.11.3

* Wed Nov 21 2007 Oden Eriksson <oeriksson@mandriva.com> 2.11.2.2-1mdv2008.1
+ Revision: 110949
- 2.11.2.2 (Minor security fixes)

* Sun Nov 11 2007 Oden Eriksson <oeriksson@mandriva.com> 2.11.2.1-1mdv2008.1
+ Revision: 107531
- 2.11.2.1

* Sat Oct 27 2007 Funda Wang <fwang@mandriva.org> 2.11.2-1mdv2008.1
+ Revision: 102583
- update to new version 2.11.2

* Thu Oct 18 2007 Oden Eriksson <oeriksson@mandriva.com> 2.11.1.2-1mdv2008.1
+ Revision: 99939
- 2.11.1.2 fixes the following issues: CVE-2007-0095, CVE-2007-0203, CVE-2007-0204,
  CVE-2007-1325, CVE-2007-1395, CVE-2007-2245, CVE-2007-4306, CVE-2007-5386

* Tue Oct 16 2007 Oden Eriksson <oeriksson@mandriva.com> 2.11.1.1-1mdv2008.1
+ Revision: 99007
- 2.11.1.1 (Minor security fixes)

* Thu Oct 11 2007 Oden Eriksson <oeriksson@mandriva.com> 2.11.1-1mdv2008.1
+ Revision: 97001
- 2.11.1

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Fix Exec command
      Remove old menu entry

* Wed Aug 22 2007 Funda Wang <fwang@mandriva.org> 2.11.0-1mdv2008.0
+ Revision: 68871
- New version 2.11.0
- Rediff patch0 (config)

* Fri Jul 20 2007 Funda Wang <fwang@mandriva.org> 2.10.3-1mdv2008.0
+ Revision: 53916
- New version

* Sat Jun 16 2007 Oden Eriksson <oeriksson@mandriva.com> 2.10.2-1mdv2008.0
+ Revision: 40253
- 2.10.2

* Tue Apr 24 2007 David Walluck <walluck@mandriva.org> 2.10.1-1mdv2008.0
+ Revision: 17770
- 2.10.1

* Mon Apr 23 2007 Oden Eriksson <oeriksson@mandriva.com> 2.10.0.2-3mdv2008.0
+ Revision: 17325
- remove the desktop-file-utils deps

