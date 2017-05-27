#! /usr/bin/env python
import sys
import yaml
import os


def parse_config(config_path):
    with open(config_path, 'r') as f:
        config = {}
        try:
            config = yaml.load(f)
        except yaml.YAMLError as e:
            print("Config parse error")
            exit(1)
        return config

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("no config_path specified")
        exit(1)
    commands = []
    config_path = sys.argv[1]
    config = parse_config(config_path)
    config = config['stack']
    prefix = config['common']['project-name']

    commands = [ None for _ in range(len(config)-1) ]

    for k, v in config.iteritems():
        if k == 'common':
            continue
        release_version = "{0}{1}{2}".format(k[0], len(k)-2, k[-1])
        if 'chart-version' in v.keys():
            command = "helm install %s --name %s-%s" % (v['chart-version'], prefix, release_version)
        if 'kub-service-name' in v.keys():
            command = "kubectl create"
        if v.get("config", ""):
            command += " -f %s/%s" % (os.path.dirname(config_path), v['config'])
        commands[v.get("order") -1 ] = command

    for cmd in commands:
        print(cmd)
