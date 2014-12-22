# smartDNS config generator
# Fabien Culpo - 2014

globalConf = """
global
  daemon
  maxconn 20000
  user haproxy
  group haproxy
  stats socket /var/run/haproxy.sock mode 0600 level admin
  log /dev/log local0 debug
  pidfile /var/run/haproxy.pid
  spread-checks 5

defaults
  maxconn 19500
  log global
  mode http
  option httplog
  option abortonclose
  option http-server-close
  option persist
  timeout connect 20s
  timeout client 120s
  timeout server 120s
  timeout queue 120s
  timeout check 10s
  retries 3

listen stats
  bind 0.0.0.0:27199
  mode http
  stats enable
  stats realm Protected\ Area
  stats uri /
  stats auth haproxy:Change-Me-Now

"""

def generate_frontend_http(urls):
  "Generate the main haproxy http frontend"

  default = """frontend f_catchall_http
  bind 0.0.0.0:80
  mode http
  option httplog
  capture request header Host len 50
  capture request header User-Agent len 150
  default_backend b_deadend_http\n\n"""

  with open('haproxy.cfg', 'a') as f:
    f.write(default)
    for url in urls:
      line = "  use_backend b_catchall_http if { hdr_dom(host) -i " + url + " }\n"
      f.write(line)

def generate_frontend_https(urls):
  "Generate the main haproxy https frontend"

  default = """frontend f_catchall_https
  bind 0.0.0.0:443
  mode tcp
  option tcplog
  tcp-request inspect-delay 5s
  tcp-request content accept if { req_ssl_hello_type 1 }
  default_backend b_deadend_https\n\n"""

  with open('haproxy.cfg', 'a') as f:
    f.write(default)
    for url in urls:
      line = "  use_backend b_catchall_https if { req_ssl_sni -i " + url + " }\n"
      f.write(line)


def generate_backend_http(urls):
  "Generate the main haproxy http backend"

  default = """\nbackend b_catchall_http
  mode http
  option httplog
  option accept-invalid-http-response\n\n"""

  with open('haproxy.cfg', 'a') as f:
    f.write(default)
    for url in urls:
      line1 = "  use-server " + url + " if { hdr_dom(host) -i " + url + " }\n"
      line2 = "  server " + url + " " + url + ":80 check inter 10s fastinter 2s downinter 2s fall 1800\n\n"
      f.write(line1)
      f.write(line2)

def generate_backend_https(urls):
  "Generate the main haproxy https backend"

  default = """\n\nbackend b_catchall_https
  mode tcp
  option tcplog\n\n"""

  with open('haproxy.cfg', 'a') as f:
    f.write(default)
    for url in urls:
      line1 = "  use-server " + url + " if { req_ssl_sni -i " + url + " }\n"
      line2 = "  server " + url + " " + url + ":443 check inter 10s fastinter 2s downinter 2s fall 1800\n\n"
      f.write(line1)
      f.write(line2)

def generate_deadends():
  "Generate deadends"

  default = """
backend b_deadend_http
  mode http
  option httplog
  option accept-invalid-http-response
  option http-server-close

backend b_deadend_https
  mode tcp
  option tcplog"""

  with open('haproxy.cfg', 'a') as f:
    f.write(default)


def main():
  with open("urls.txt","r") as u:
    urls = u.read().splitlines()
  with open('haproxy.cfg', 'w') as f:
    f.write(globalConf)
  generate_frontend_http(urls)
  generate_backend_http(urls)
  generate_frontend_https(urls)
  generate_backend_https(urls)
  generate_deadends()

if __name__ == '__main__':
    main()