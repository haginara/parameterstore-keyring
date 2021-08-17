"""This package provides a keyring backend that is backed by an AWS Parameter Store

Example
=======

"""

from functools import lru_cache
import logging

import boto3
import keyring
from keyring.errors import InitError, PasswordDeleteError

__version__ = '0.0.2'

logger = logging.getLogger(__name__)


class ParameterStoreKeyring(keyring.backend.KeyringBackend):
    """A keyring backend backed by an AWS parameter store."""

    prioirity = 0.5

    def __init__(self, profile_name=None, region_name=None):
        super(ParameterStoreKeyring, self).__init__()
        if region_name is None:
            raise Exception("region_name does not set")
        self._profile_name = profile_name
        self._region_name = region_name

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
        response = ssm.put_parameter(
            Name=self.__make_name(service, username),
            Description='Stored by keyring',
            Value=password,
            Overwrite=True,
            Type='SecureString',
            #KeyId=""
        )
        return response

    def get_password(self, service, username):
        ssm=self.get_ssm()
        response = ssm.get_parameter(
            Name=self.__make_name(service, username),
            WithDecryption=True
        )
        return response['Parameter']['Value']

    def delete_password(self, service, username):
        pass

