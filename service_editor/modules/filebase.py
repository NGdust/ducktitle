import os
import boto3
from botocore.client import Config
from google.cloud import storage


class FirebaseTransport:
    def upload(self):
        raise NotImplementedError


class FirebaseStorageTransport(FirebaseTransport):

    def __init__(self, FIREBASE_STORAGE_BUCKET, credentials='config-google.json',
                 user_email=None, from_filename=None, to_filename=None):
        self.user_email = user_email
        self.to_filename = to_filename
        self.from_filename = from_filename
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
        self.client = storage.Client()
        self.FIREBASE_STORAGE_BUCKET = FIREBASE_STORAGE_BUCKET
        self.bucket = self.client.get_bucket(FIREBASE_STORAGE_BUCKET)

    def upload(self):
        blob = self.bucket.blob(self.user_email + '/' + self.to_filename)
        blob.upload_from_filename(self.from_filename)
        return f"gs://{self.FIREBASE_STORAGE_BUCKET}/{self.user_email}/{self.to_filename}"


class WassabiStorageTransport:
    def __init__(self, AWS_ACCESS_KEY, AWS_SECRET_KEY,
                 user_email=None, from_filename=None):
        self.user_email = user_email
        self.endpoint_url = 'https://s3.us-west-1.wasabisys.com'
        self.from_filename = from_filename
        self.bucket = 'suptitle'
        self.s3 = boto3.resource(
                                    's3',
                                    endpoint_url=self.endpoint_url,
                                    aws_access_key_id=AWS_ACCESS_KEY,
                                    aws_secret_access_key=AWS_SECRET_KEY,
                                    config=Config(signature_version='s3v4')
                                )

    def upload(self):
        data = open(self.from_filename, 'rb')
        filename = self.from_filename.rsplit('/', 1)[-1]
        key_file = self.user_email + '/' + filename

        self.s3.Bucket(self.bucket).put_object(ACL='public-read', Key=key_file, Body=data)
        url_video_in_storage = f'https://{self.bucket}.s3.us-west-1.wasabisys.com/{key_file}'

        if not self.check_user_file(url_video_in_storage):
            raise Exception(f"Couldn't upload the video: {filename}")

        return url_video_in_storage

    def list_files(self):
        listObjSummary = self.s3.Bucket(self.bucket).objects.all()
        for obj in listObjSummary:
            print(f'https://{self.bucket}.s3.us-west-1.wasabisys.com/{obj.key}')

    def list_user_files(self):
        listObjSummary = self.s3.Bucket(self.bucket).objects.all()
        for obj in listObjSummary:
            if self.user_email in obj.key:
                print(f'https://{self.bucket}.s3.us-west-1.wasabisys.com/{obj.key}')

    def clear_all_bucket(self):
        listObjSummary = self.s3.Bucket(self.bucket).objects.all()
        for obj in listObjSummary:
            obj.delete()
            print(f'Deleted https://{self.bucket}.s3.us-west-1.wasabisys.com/{obj.key}')

    def clear_user_bucket(self, user):
        listObjSummary = self.s3.Bucket(self.bucket).objects.all()
        for obj in listObjSummary:
            if user in obj.key:
                obj.delete()
                print(f'Deleted from {user}: https://{self.bucket}.s3.us-west-1.wasabisys.com/{obj.key}')

    def check_user_file(self, url):
        url = url.rsplit('/', 1)[-1]
        listObjSummary = self.s3.Bucket(self.bucket).objects.filter(Prefix=f'{self.user_email}/{url}')
        for obj in listObjSummary:
            if self.user_email in obj.key or url in obj.key:
                print(f'https://{self.bucket}.s3.us-west-1.wasabisys.com/{obj.key}')
                return True
        return False


if __name__ == '__main__':
    user_email = 'kvando.test@mail.ru'
    from_filename = '/home/kvando/Загрузки/iso.mp4'
    transport = WassabiStorageTransport(user_email=user_email, from_filename=from_filename)
    # transport.clear_user_bucket(user_email)

    transport.list_user_files()

    url = transport.upload()
    print(url)

    url = url.rsplit('/', 1)[-1]
    print(url)

    if transport.check_user_file(url):
        print('File exists in FileStorage')
    else:
        print('File not exists in FileStorage')