#!/usr/bin/env python
#coding:utf-8 

from enum import Enum
import warnings,os,platform,sys,time,re,shutil,threading,subprocess,uuid,posixpath,socket,configparser,getopt
from socketserver import ThreadingMixIn
import http.server,six,mimetypes,html
import urllib.error,urllib.parse,urllib.request



try:
    import numpy as np
except:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host tuna.tsinghua.edu.cn numpy ')
    import numpy as np

try:
    import qrcode
except:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host tuna.tsinghua.edu.cn qrcode ')
    import qrcode

try:
    import PIL
except:
    os.system('pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host tuna.tsinghua.edu.cn pillow ')

try:
    from io import StringIO
except ImportError:
    from io import StringIO


origin_settings = dict(
    host = "0.0.0.0",
    port = "34433",
    external_address = None,
    config = os.path.join(sys.prefix, 'config', 'app.cfg'),
    exchange_dir = os.path.join(os.getcwd(), ".exch")
)

class Util(object):
    @staticmethod
    def getip():
        match_ip_dict = {}
        ipconfig_result_list = os.popen('ipconfig').readlines()
        for i in range(0, len(ipconfig_result_list)):
            if re.search(r'IPv4 地址', ipconfig_result_list[i]) != None:
                match_ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
                                     ipconfig_result_list[i]).group(0)
                for j in range(3, 7):
                    if re.search(r"无线局域网适配器", ipconfig_result_list[i - j]) != None:
                        match_ip_dict[ipconfig_result_list[i - j]] = match_ip
        ip_dict = match_ip_dict
        for i in ip_dict:
            return ip_dict[i]

    @staticmethod
    def visit(url):
        opener = urllib.request.urlopen(url, None, 3)
        if url == opener.geturl():
            str = opener.read()
        return re.search(r'(\d+\.){3}\d+', str).group(0)

    @staticmethod
    def sizeof_fmt(num):
        for x in ['bytes', 'KB', 'MB', 'GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

    @staticmethod
    def modification_date(filename):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filename)))

class Profile(object):
    def __init__(self):
        for name,val in origin_settings.items():
            setattr(self, name, val)

        self.serveraddr = self.show_tips()

    def show_tips(self):
        try:
            port = int(self.port)
            if not 1024 < port < 65535:
                raise RuntimeError(f"Out of range: 1024 < port < 65535")
        except ValueError:
            # print(value1, ..., sep=' ', end='\n', file=sys.stdout, flush=False)
            print("The 'port' argument must be an integer", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"{e}", file=sys.stderr)
            sys.exit(1)

        if not self.host:
            if platform.system() == "windows".lower():
                self.host = Util.getip()

        iu = f'http://{self.host}:{str(port)}'
        eu = iu if not self.external_address else f'http://{self.external_address}'
        print(f"Listen to '{iu}'")


        print(f"Now, you can go to visit '{eu}' or scan the following QR code")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1
        )
        qr.add_data(eu)
        qr.make(fit=True)
        img = qr.make_image()
        img2 = np.array(img.convert('L'))
        d = {255: '@@', 0: '  '}
        rows, cols = img2.shape
        for i in range(rows):
            for j in range(cols):
                print(d[img2[i, j]], end='')
            print('')
        return (self.host, port)

class ThreadingServer(ThreadingMixIn, http.server.HTTPServer):
    @classmethod
    def create_server(cls, profile, server):
        cls.__profile = profile
        return ThreadingServer(cls.get_profile('serveraddr'), server)

    @classmethod
    def get_profile(cls, key, default_value = None):
        return getattr(cls.__profile, key, default_value)

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        f = self.send_head()
        if f:
            for i in f.readlines():
                if isinstance(i, str):
                    self.wfile.write(i.encode("utf-8"))
                else:
                    self.wfile.write(i)
            f.close()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        r, info, dest = self.deal_post_data()
        print(f"{info} - client({str(self.client_address)}),result({str(r)}),output({dest})")
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write('<meta name="viewport" content="width=device-width" charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">')
        f.write("<html>\n<title>上传结果</title>\n")
        f.write("<body>\n<h2>文件上传</h2>")
        if r:
            f.write('<strong style="color:#00FF00">成功</strong>\n')
        else:
            f.write('<strong style="color:#FF0000">失败</strong>\n')
        f.write("<hr>\n")
        f.write(info)
        f.write("</br><a href=\"%s\">点击返回</a>" % self.headers['referer'])
        f.write("<hr><small>Powered By: gaowanliang                       ")
        f.write("</small></body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            for i in f.readlines():
                self.wfile.write(i.encode("utf-8"))
            f.close()

    def deal_post_data(self):
        boundary = str(
            self.headers["Content-Type"].split("=")[1]).encode("utf-8")
        remainbytes = int(self.headers['Content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        filename = re.findall(
            r'Content-Disposition.*name="file"; filename="(.*)"'.encode('utf-8'), line)
        if not filename:
            return (False, "Can't find out file name...")
        path = str(self.translate_path(self.path)).encode('utf-8')
        osType = platform.system()
        try:
            if osType == "Linux":
                output_file = os.path.join(path, filename[0].decode('gbk').encode('utf-8'))
            else:
                output_file = os.path.join(path, filename[0])
        except Exception as e:
            return (False, "文件名请不要用中文，或者使用IE上传中文名的文件。{}" .format(e))
        while os.path.exists(output_file):
            output_file += "_".encode("utf-8")
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            of = open(output_file, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'.encode("utf-8")):
                    preline = preline[0:-1]
                of.write(preline)
                of.close()
                return (True, f"Upload '{filename}' successfully", output_file)
            else:
                of.write(preline)
                preline = line
        return (False, "Unexpect ends of data.", None)

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def get_exchange_diretory(self):
        p = ThreadingServer.get_profile("exchange_dir")
        if not os.path.exists(p):
            os.makedirs(p)
        return p

    def list_directory(self, path):
        exchage_root = self.get_exchange_diretory()
        try:
            l = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        l.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = html.escape(urllib.parse.unquote(self.path))
        f.write('<!DOCTYPE html>')
        f.write('<meta name="viewport" content="width=device-width" charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">')
        f.write("<html>\n<title>内网传输</title>\n")
        f.write("<body>\n<h2>目录清单 位于%s</h2>\n" % displaypath)
        f.write("<hr>\n")
        f.write("<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write("<input name=\"file\" type=\"file\"/>")
        f.write("<input type=\"submit\" value=\"上传\"/>")
        f.write(
            "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp")
        f.write("<input type=\"button\" value=\"主目录\" onClick=\"location='/'\">")
        f.write("</form>\n")
        f.write(
            '<h2 style="color:#FF0000">请先选择完文件再点上传，不这样做的话可能会出现奇怪的情况</h2><hr>\n<ul>\n')
        for name in l:
            fullname = os.path.join(path, name)
            colorName = displayname = linkname = name
            if os.path.isdir(fullname):
                colorName = '<span style="background-color: #CEFFCE;">' + name + '/</span>'
                displayname = name
                linkname = name + "/"
            if os.path.islink(fullname):
                colorName = '<span style="background-color: #FFBFFF;">' + name + '@</span>'
                displayname = name
            # print('xx'*30, path, name, fullname)
            
            # filename = os.path.join(exchage_root, os.path.realpath(path, exchage_root), displayname)
            # print('xx'*30, filename)
            f.write('<table><tr><td width="60%%"><a href="%s">%s</a></td><td width="20%%">%s</td><td width="20%%">%s</td></tr>\n'
                    % (urllib.parse.quote(linkname), colorName,
                        Util.sizeof_fmt(os.path.getsize(fullname)), Util.modification_date(fullname)))
        f.write("</table>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = self.get_exchange_diretory()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })

def show_usage():
    print(f'''
    Usage: {sys.argv[0]} [OPTION]...
    Launch file viewer server

    Options:
      -c,--config=<path>        The configuration file
      -w,--exchange-dir=<path>  The root directory for exchanging
      -v,--version              Show version
    ''')

def show_version():
    import pkg_resources
    print(pkg_resources.get_distribution("construct").version)

def test(HandlerClass=SimpleHTTPRequestHandler, ServerClass=http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],'-h-v-c:',['help', 'version', 'config='])
        for opt,optval in opts:
            if opt in ('-h','--help'):
                show_usage()
                sys.exit()
            if opt in ('-v','--version'):
                show_version()
                sys.exit()
            if opt in ('-w', '--exchange-dir'):
                origin_settings.update(exchange_dir = optval)
            if opt in ('-c','--config'):
                origin_settings.update(config = optval)

            # -w,--exchange-dir

        if os.path.exists(origin_settings.get('config')):
            parser = configparser.ConfigParser()
            parser.read(origin_settings.get('config'), encoding='utf-8')

            if parser.has_section('common'):
                print( parser.items(section='common'))
                for k,v in parser.items(section='common'):
                    origin_settings.update({ k : v.strip()})

        srvr = ThreadingServer.create_server(
            Profile(),
            SimpleHTTPRequestHandler
        )
        srvr.serve_forever()
    except KeyboardInterrupt:
        print("Done!")


if __name__ == '__main__':
    main()
