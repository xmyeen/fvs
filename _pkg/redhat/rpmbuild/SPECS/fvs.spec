Name: fvs
Version: 1.0.0
Release: 1%{?dist}

Group: Applications/Internet
License: MIT
URL: https://github.com/xmyeen/fvs
Source0: %(cd %{_topdir}/SOURCES; find . -iname "%{name}*" | xargs basename)
BuildArch: noarch
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
# BuildRequires: python3
Prefix: %{_prefix}/local/lib
Summary: File Viewer Server

%description
File Viewer Server

%define app_root %{_prefix}/local/lib/%{name}
%define cfg_root %{_sysconfdir}/sysconfig/%{name}
%define venv_root %{app_root}/.venv
%define rc_root %{app_root}/rc
%define deamon_cmd "fvsctl"

#在执行rpm时完成相关文件资源的预处理
%prep

%build
cp -rf %{SOURCE0} .
pip3 download %{SOURCE0} -d .

%pre

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{rc_root} %{buildroot}%{venv_root}
find %{_builddir} -iname "*.whl" | xargs -i install -v {} %{buildroot}%{rc_root}

%post
py_checking_paths="python /usr/bin/python /usr/local/bin/python python3 /usr/bin/python3 /usr/local/bin/python3"
pycmd=""

for rcfile in %{getenv:HOME}/.bashrc
do
    if [ -f "$rcfile" ]
    then
        echo "Load environment file: $rcfile"
        source $rcfile
    fi
    for c in ${py_checking_paths}
    do
        type ${c} >/dev/null 2>&1 &&
        [ "3" == "$(${c} --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)" ] &&
        pycmd="${c}" &&
        break 2
    done
done

if [ -z "${pycmd}" ]
then
    echo >&2 "I require python3 but it's not installed.  Aborting."
    exit 1
else 
    echo "Use $(${pycmd} --version)"
fi

echo "Install %{name}, now"

${pycmd} -m venv --clear %{venv_root}
source %{venv_root}/bin/activate
pip install -U --force-reinstall --no-index --pre --find-links=%{rc_root} %{name}
pip freeze > %{app_root}/reqirements.txt
type %{deamon_cmd} >/dev/null 2>&1 &&
%{deamon_cmd} -i
deactivate

%clean

%preun

%postun
if [ "$1" = "0" ] ; then
    if [ -f "%{venv_root}/bin/%{deamon_cmd}" ]
    then
        source %{venv_root}/bin/activate
        %{deamon_cmd} -u
        deactivate
    fi

    for d in %{app_root} %{cfg_root}
    do
        if [ -e $d ]
        then
            rm -vrf $d
        fi
    done
fi

%files
%defattr(-,root,root)
%{app_root}

%doc

%changelog