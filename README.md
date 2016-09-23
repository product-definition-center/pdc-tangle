# PDC-Tangle

### Overview

PDC-Tangle is a command-line tool written in Python that queries PDC to present
an artifact's recursive dependencies in a tree-like structure.

### Usage

To query the recursive dependencies of the python RPM:

```bash
python pdc-tangle.py python
```

To specify the PDC server that PDC-Tangle queries:

```bash
python pdc-tangle.py -s pdc.stg.fedoraproject.org python
```

To specify the type of dependencies that PDC-Tangle queries for:

```bash
python pdc-tangle.py -d RPMRequires -d RPMBuildRequires python
```

To specify the release that the query targets:

```bash
python pdc-tangle.py -r fedora-26 python
```

To view the help:

```bash
python pdc-tangle.py --help
```

### Installation

#### Vagrant

```bash
vagrant up
vagrant ssh
source /opt/pdc-tangle/env/bin/activate
cd /opt/pdc-tangle/src
```

#### virtualenv on Fedora 24

```bash
dnf install -y python python-virtualenv gcc python-devel krb5-devel libffi-devel redhat-rpm-config
virtualenv /opt/pdc-tangle/env
source /opt/pdc-tangle/env/bin/activate
pip install -r /opt/pdc-tangle/src/requirements.txt
```
