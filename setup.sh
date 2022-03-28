#!/bin/bash

PYTHON_CMD="python3"

PIP_COMMAND_OPTS="-i https://mirrors.cloud.aliyuncs.com/pypi --trusted-host mirrors.cloud.aliyuncs.com -U"

BUILD_ROOT=".build"
DIST_ROOT=".dist"

# 清理
LAST_BUILDING_DIRS="${BUILD_ROOT} ${DIST_ROOT}"
for i in ${LAST_BUILDING_DIRS}
do
  if [ -e $i ];then rm -rf $i; fi
done
mkdir -p ${DIST_ROOT} ${BUILD_ROOT}

# 检查PYTHON命令
type ${PYTHON_CMD} >/dev/null 2>&1 || { echo >&2 "I require python3 but it's not installed.  Aborting."; exit 1; }
if [ "$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)" == "3" ]; then PYTHON_CMD="python"; fi

${PYTHON_CMD} -m pip install ${PIP_COMMAND_OPTS} pip setuptools wheel

build_readhat(){
RPMBUILD_ROOT="${PWD}/.rpmbuild"
mkdir -p ${RPMBUILD_ROOT}/{RPMS,SOURCES,SPECS,SRPMS}

RPMBUILD_RPM_ROOT="${RPMBUILD_ROOT}/RPMS/"
RPMBUILD_SRPM_ROOT="${RPMBUILD_ROOT}/SRPMS/"
RPMBUILD_SOURCE_ROOT="${RPMBUILD_ROOT}/SOURCES/"

#1. 编译rpm包
${PYTHON_CMD} setup.py bdist_wheel -b ${BUILD_ROOT}

#2. 提取rpm成果物，组织rpmbuild目录
DIST_FILEPATH="$(find dist/ -iname "*.whl" | head -n 1)"
if [ -z "${DIST_FILEPATH}" ];then echo >&2 "Package failed.  Aborting."; exit 1; fi
mv -f ${DIST_FILEPATH} ${RPMBUILD_SOURCE_ROOT}

rpmbuild --clean -bb _pkg/redhat/rpmbuild/SPECS/fvs.spec --define "_topdir ${RPMBUILD_ROOT}"

find ${RPMBUILD_RPM_ROOT} -iname "*.rpm" | xargs -i mv -v -f {} ${DIST_ROOT}
rm -rf ${RPMBUILD_ROOT}
}

build_readhat
