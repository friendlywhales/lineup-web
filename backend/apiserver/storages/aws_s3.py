
from storages.backends.s3boto import S3BotoStorage


MediaStorage = lambda: S3BotoStorage(location='uploads')
