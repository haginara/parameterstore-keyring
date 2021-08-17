Keyring Backend - AWS ParameterStore
====================================

## Example

```python
import keyring
from paramstore_keyring import ParameterStoreKeyring

# region_name parameter is required
keyring.set_keyring(ParameterStoreKeyring(region_name='us-west-2'))

# Set password
# Parameters: service_name, username, password
# It tries to put parameter on /Dev/Production/WestProject/test-secret
keyring.set_password('Dev/Production/WestProject', 'test-secret', 'Secret Value')

# Get Password
# Parameters: service_name, username
# It tries to get parameter on /Dev/Production/WestProject/test-secret
keyring.get_password('Dev/Production/WestProject', 'test-secret')
```

## Todo

- [ ] Load the AWS crednetial and configs from Environment variable
- [ ] implement delete_password method