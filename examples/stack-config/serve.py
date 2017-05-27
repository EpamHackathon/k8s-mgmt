#! /usr/bin/env python
import sys
import yaml
import os
import jinja2
from commands import *

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


def parse_config(config_path):
    with open(config_path, 'r') as f:
        config = {}
        try:
            config = yaml.load(f)
        except yaml.YAMLError as e:
            print("Config parse error")
            exit(1)
        return config


def run(cmd):
    status, text = getstatusoutput(cmd)
    if status == 0:
        return yaml.load(text)
    else:
        return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("no config_path specified")
        exit(1)

    task = sys.argv[1]

    commands = []
    config_path = sys.argv[2]
    config = parse_config(config_path)
    config = config['stack']
    prefix = config['common']['project-name']
    # commands = [None for _ in range(len(config)-1)]
    commands = [None for _ in range(100)]

    if task == "helm":
        for k, v in config.iteritems():
            if k == 'common':
                continue

            release_version = "{0}{1}{2}".format(k[0], len(k)-2, k[-1])

            if "chart-version" in v.keys():
                # print(v['chart-version'])
                command = "helm install %s --name %s-%s" % (v['chart-version'], prefix, release_version)
                if v.get("config", ""):
                    command += " -f %s/%s" % (os.path.dirname(config_path), v['config'])

                index = v.get("order")
                if index > 0:
                    commands[index-1] = command

    if task == "ingress":
        for k, v in config.iteritems():
            if k == 'common':
                continue

            release_version = "{0}{1}{2}".format(k[0], len(k)-2, k[-1])
            if 'kub-service-name' in v.keys():

                # print(v['config'][-3:])
                if v['config'][-3:] == ".j2":
                    command = "kubectl create"
                    hosts = []

                    domain_name = config["common"]["domain-name"]
                    project_name = config["common"]["project-name"]

                    for k, val in config.iteritems():
                        if val.get("ingress", False):
                            hosts.append({
                                "name": "{0}.{1}".format(k, domain_name),
                                "service_port": val.get("service_port"),
                                "service_name": "{0}-{1}-{2}".format(project_name, "{0}{1}{2}".format(k[0], len(k)-2, k[-1]), val.get("service_name")),
                                "port": val.get("service_port")
                            })
                    # print(hosts)
                    #                         hackathon-n3x-nginx-ingress-controller
                    # ip = run("kubectl get svc nginx-ingress-test-nginx-ingress-controller -o yaml")["status"]["loadBalancer"]["ingress"][0]["ip"]
                    ip = run("kubectl get svc hackathon-n3x-nginx-ingress-controller -o yaml")["status"]["loadBalancer"]["ingress"][0]["ip"]

                    context = {
                        "hosts": hosts,
                        "some_ip": ip
                    }

                    rendered_config_file = "/tmp/rendered_{0}".format(os.path.basename(v['config'][:-3]))
                    result = render("{0}/{1}".format(os.path.dirname(config_path), v['config']), context)
                    rendered = open(rendered_config_file, "w")
                    rendered.write(result)
                    rendered.close()

                    command += " -f {0}".format(rendered_config_file)
                else:
                    command = "kubectl create -f {0}/{1}".format(os.path.dirname(config_path), v['config'])

                index = v.get("order")

                if index > 0:
                    commands[index-1] = command

    if task == "dns":
        for k, v in config.iteritems():
            if k == 'common':
                continue

            # gcloud dns record-sets transaction start -z=hackaton
            # gcloud dns record-sets transaction add -z=hackaton --name="release.hack.bomba.by." --type=A --ttl=300 "$(kubectl get svc | grep nginx-ingress-controller | awk '{print $3}')"
            # gcloud dns record-sets transaction execute -z=hackaton

            if "assign_dns" in v.keys():
                ix = 1
                commands[0] = "gcloud dns record-sets transaction start -z=hackaton"
                domain_name = config["common"]["domain-name"]
                ip = run("kubectl get svc nginx-ingress-test-nginx-ingress-controller -o yaml")["status"]["loadBalancer"]["ingress"][0]["ip"]
                for item in v["assign_dns"]:
                    commands[ix] = "gcloud dns record-sets transaction add -z=hackaton --name=\"{0}.{1}.\" --type=A --ttl=300 {2}".format(item, domain_name, ip)
                    ix = ix + 1
                commands[ix] = "gcloud dns record-sets transaction execute -z=hackaton"


    for item in commands:
            if item:
                print(item)