
from django.core.files.storage import Storage

"""

1.您的自定义存储系统必须是以下的子类 ：django.core.files.storage.Storage
2.Django必须能够在没有任何参数的情况下实例化您的存储系统。
    这意味着任何设置都应该来自：django.conf.settings
3.您的存储类必须实现_open()和_save() 方法，
    以适合您的存储类中的任何其他方法一起。请参阅下面的这些方法。
4.您的存储类必须是可解构的， 以便在迁移中的字段上使用时可以对其进行序列化。
只要您的字段具有可自行序列化的参数，
就 可以使用 django.utils.deconstruct.deconstructible类装饰器
（这就是Django在FileSystemStorage上使用的）

"""
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible
from mall import settings


@deconstructible
class MyStorage(Storage):

    # 初始化的时候 有任何配置信息 都设置为 默认值
    def __init__(self, config_path=None,ip=None):
        if not config_path:
            config_path = settings.FDFS_CLIENT_CONF
        self.config_path = config_path

        if not ip:
            ip = settings.FDFS_URL
        self.ip = ip

    # open 打开文件(图片)
    # Fdfs 是通过 HTTP来访问我们的图片资源的,不需要打开
    # http://192.168.229.148:8888/group1/M00/00/02/wKjllFx4r_aAJyv2AAGByoOJNyU855.jpg

    def _open(self, name, mode='rb'):
        pass

    # save 保存
    # 保存是通过 Fdfs来实现保存的,所以我们要在save中实现保存操作
    def _save(self, name, content, max_length=None):
        # name, content, max_length=None

        # name: 图片名字
        # content: 图片资源
        # max_length: 最大长度

        # 1.创建上传 的客户端
        # client = Fdfs_client('utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)

        client = Fdfs_client(self.config_path)

        # 2.获取图片  我们不能通过name找到图片,所以通过content来获取图片内容
        # 读取的是 图片的二进制
        data = content.read()
        # 3.上传
        # buffer 二进制
        result = client.upload_by_buffer(data)
        # result 就是上传之后的返回值

        # 4.根据上传的状态获取 remote file_id
        """
        {'Group name': 'group1',
        'Remote file_id': 'group1/M00/00/02/wKjllFx42-6AW-JBAAGByoOJNyU783.jpg',
        'Status': 'Upload successed.',
        'Local file name': '/home/python/Desktop/images/2.jpg',
        'Uploaded size': '96.00KB',
        'Storage IP': '192.168.229.148'}
        """
        if result.get('Status') == 'Upload successed.':
            #上传成功,返回 remote file_id
            file_id = result.get('Remote file_id')
        else:
            raise Exception('上传失败')

        # 我们需要把 remote file_id 返回回去
        # 系统要使用
        return file_id

    # exists 是否存在
    # Fdfs 已经帮我们做了 重名的处理,所以我们不需要判断 图片是否重复
    # 直接上它上传就可以
    def exists(self, name):

        return False

    # url 默认是把 name返回回去,
    # 在Fdfs中 name其实就是 remote file_id
    # 但是我们在访问图片的时候  需要自己再添加 http://ip:port/ + name
    # 所以我们重写 url方法,添加 http://ip:prot/ + name
    def url(self, name):
        # return 'http://192.168.229.148:8888/' + name
        # return settings.FDFS_URL + name
        return self.ip + name

        # return name
        # pass



