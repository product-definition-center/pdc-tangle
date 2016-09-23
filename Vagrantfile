# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
    dnf install -y python python-virtualenv gcc python-devel krb5-devel libffi-devel redhat-rpm-config
    virtualenv /opt/pdc-tangle/env
    source /opt/pdc-tangle/env/bin/activate
    pip install -r /opt/pdc-tangle/src/requirements.txt
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "boxcutter/fedora24"
  config.vm.synced_folder "./", "/opt/pdc-tangle/src"
  config.vm.provision "shell", inline: $script
end
