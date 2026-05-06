import pymysql
pymysql.install_as_MySQLdb()

# Override version for Django compatibility
pymysql.version_info = (2, 2, 1)
pymysql.__version__ = "2.2.1"