import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from pandas.io import pickle
import os

class S3DataManager:
    def __init__(self):
        self.BUCKET_NAME = 'pydash-app-data'
        self.s3 = boto3.client('s3'
        # config=Config(signature_version='s3v4')
        )
        self.filteredSatData = False
        self.filteredVesData = False

    def load_data(self, s3_path, s3_usecols=[], loc_usecols=[]):
        try:
            print('>>> Loading data: {0}'.format(s3_path))
            data = self._get_s3_data(s3_path)
            if len(s3_usecols) > 0:
                data = data[s3_usecols]
            print('>>> Load complete')
        except NoCredentialsError:

            raise NameError('Credentials not found. No data')

        return data

    def _get_s3_data(self, key):

        if os.getenv('LOCAL_DEV_MODE') == 1:
            print(">>> local dev mode, reading file locally")
            return pd.read_pickle('/home/brendan/projects/cms/r2py/df_inpatient.pkl', compression='xz')

        print(">>> getting file from s3")
        obj = self.s3.get_object(Bucket=self.BUCKET_NAME, Key=key)

        print(">>> file downloaded, reading it in")

        body = obj['Body']
        data = pd.read_pickle(body, compression='xz')
        return data


