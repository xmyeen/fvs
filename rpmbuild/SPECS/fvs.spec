Name: filesvr
Version: 1.0.0
Release: 1%{?dist}

Group: Applications/Internet
License: MIT
Source0: %{name}-%{Version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: python3

%define python_path /tmp/python/
%define etc_path /tmp/etc/
%deinf config_file filesvr

#在执行rpm时完成相关文件资源的预处理
%prep
tar -cvf ../SOURCES/%{Source0} ../SOURCES/*.txt
if [ ! -d "%{python_path}" ]; then
    mkdir -p "%{python_path}"
if [ ! -d "%{python_path}" ]; then
    mkdir "%{etc_path}"
fi

tar -xvf ../SOURCES/%{Source0} -C %{python_path}

%build
cp ../SOURCES/%{config_file} %{etc_path}
chmod 755 /tmp/etc/%{config_file}
./configure
make

%install
make install

%clean
rm -rf %{build_root}

%files

%doc

%postun
if [ "%1" = "0" ]; then
    echo 'uninstall start ...'
    rm -rf %{python_path} %{etc_path}
    echo 'uninstall done!'
fi


%changlog