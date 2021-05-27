import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError

class S3DataManager:
    def __init__(self):
        self.BUCKET_NAME = 'pydash-app-data'
        self.s3 = boto3.client('s3'
        # aws_access_key_id='',
        # aws_secret_access_key='',
        # config=Config(signature_version='s3v4')
        )
        self.filteredSatData = False
        self.filteredVesData = False

    def load_data(self, s3_path, local_path, s3_usecols=[], loc_usecols=[]):
        try:
            print('---')
            print('Attempting to download s3 data: {0}'.format(s3_path))
            data = self._get_s3_data(s3_path)
            if len(s3_usecols) > 0:
                data = data[s3_usecols]
            print('Download complete.')
        except:# NoCredentialsError:
            # print('Credentials not found. Loading local CSV instead.')
            # data = pd.read_csv(local_path, low_memory=False)
            # if len(loc_usecols) > 0:
            #     data = data[loc_usecols]
            # print('Load complete.')
            
            print('Credentials not found. No data')

        return data

    def _get_s3_data(self, key):
        obj = self.s3.get_object(Bucket=self.BUCKET_NAME, Key=key)
        return pd.read_csv(obj['Body'])

    
