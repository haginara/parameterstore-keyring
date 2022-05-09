"""This package provides a keyring backend that is backed by an AWS Parameter Store

Example
=======

"""

from functools import lru_cache
import os
import logging

import boto3
import keyring
from keyring.errors import InitError, PasswordDeleteError

__version__ = '0.0.3'

logger = logging.getLogger(__name__)


class ParameterStoreKeyring(keyring.backend.KeyringBackend):
    """A keyring backend backed by an AWS parameter store."""

    prioirity = 0.5

    def __init__(self, profile_name=None, region_name=None, key_id=None):
        super(ParameterStoreKeyring, self).__init__()
        if region_name is None:
            raise Exception("region_name does not set")
        self._profile_name = profile_name
        self._region_name = region_name
        self.__key_id = os.environ.get('AWS_PARAMETER_STORE_KEY_ID', key_id)

    @lru_cache(maxsize=1)
    def get_ssm(self):
        try:
            session = boto3.session.Session(profile_name=self._profile_name, region_name=self._region_name)
            ssm = session.client('ssm')
        except Exception as e:
            logger.error("Failed to get ssm client: %s", e)
        return ssm

    def __make_name(self, service, username):
        if not username:
            name = service
        else:
            name = '/'+'/'.join([service, username])

        return name

    def set_password(self, service, username, password):
        ssm = self.get_ssm()
        params = {
            "Name": self.__make_name(service, username),
            "Description": 'Stored by keyring',
            "Value": password,
            "Overwrite": True,
            "Type": 'SecureString',
        }
        if self.__key_id:
            params["KeyId"] = self.__key_id
        response = ssm.put_parameter(**params)
        return response

    def get_password(self, service, username):
        """
        Get the password in AWS Parameter store
        """
        ssm=self.get_ssm()
        response = ssm.get_parameter(
            Name=self.__make_name(service, username),
            WithDecryption=True
        )
        return response['Parameter']['Value']

    def delete_password(self, service, username):
        """
        Delete the password in AWS Parameter Store
        """
        ssm = self.get_ssm()
        response = ssm.delete_parameter(
            Name=self.__make_name(service, username)
        )
        return response

