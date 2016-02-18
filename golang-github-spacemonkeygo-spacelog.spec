%{?scl:%scl_package %{name}}

%if 0%{?fedora} || 0%{?rhel} == 6|| 0%{?rhel} == 7
%global with_devel 1
%global with_bundled 0
%global with_debug 0
# No tests provided
%global with_check 0
%global with_unit_test 0
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%define copying() \
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7 \
%license %{*} \
%else \
%doc %{*} \
%endif

%global provider        github
%global provider_tld    com
%global project         spacemonkeygo
%global repo            spacelog
# https://github.com/spacemonkeygo/spacelog
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          ae95ccc1eb0c8ce2496c43177430efd61930f7e4
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           %{?scl_prefix}golang-%{provider}-%{project}-%{repo}
Version:        0
Release:        0.2.git%{shortcommit}%{?dist}
Summary:        Hierarchical, leveled, and structured logging library for Go
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
BuildRequires: %{?scl_prefix}golang(github.com/spacemonkeygo/flagfile/utils)
%endif

Requires:      %{?scl_prefix}golang(github.com/spacemonkeygo/flagfile/utils)

Provides:      %{?scl_prefix}golang(%{import_path}) = %{version}-%{release}
Provides:      %{?scl_prefix}golang(%{import_path}/setup) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build
%{?scl:scl enable %{scl} - << "EOF"}

%{?scl:EOF}
%install
%{?scl:scl enable %{scl} - << "EOF"}
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
olddir=$(pwd)
pushd %{buildroot}/%{gopath}/src/%{import_path}
for file in $(find . -type d) ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$file" >> ${olddir}/devel.file-list
done
popd
echo "%%dir %%{gopath}/src/%{provider}.%{provider_tld}/%{project}" >> devel.file-list
echo "%%dir %%{gopath}/src/%{provider}.%{provider_tld}" >> devel.file-list

sort -u -o devel.file-list devel.file-list
%endif

%{?scl:EOF}
%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%ifarch 0%{?gccgo_arches}
function gotest { %{gcc_go_test} "$@"; }
%else
%if 0%{?golang_test:1}
function gotest { %{golang_test} "$@"; }
%else
function gotest { go test "$@"; }
%endif
%endif

export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%endif

%if 0%{?with_devel}
%files devel -f devel.file-list
%copying LICENSE
%doc README.md
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%copying LICENSE
%doc README.md
%endif

%changelog
* Wed Feb 3 2016 Marek Skalicky <mskalick@redhat.com> - 0-0.3.gitae95ccc
- Fixed directory ownership

* Mon Aug 10 2015 Fridolin Pokorny <fpokorny@redhat.com> - 0-0.2.gitae95ccc
- Update spec file to spec-2.0
  resolves: #1250513

* Mon Jun 15 2015 Marek Skalicky <mskalick@redhat.com> - 0-0.1.gitae95ccc
- First package for Fedora
  resolves: #1232231

