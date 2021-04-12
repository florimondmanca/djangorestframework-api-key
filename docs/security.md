# Security

## Implementation details

### Key generation scheme

An API key is composed of two items:

- A prefix `P`, which is a generated string of 8 characters.
- A secret key `SK`, which is a generated string of 32 characters.

The generated key that clients use to [make authorized requests](#making-authorized-requests) is `GK = P.SK`. It is treated with the same level of care as passwords:

- Only a hashed version is stored in the database. The hash is computed using the default password hasher. [^1]
- The generated key is shown only once to the client upon API key creation.

[^1]: All hashers provided by Django should be supported. This package is tested against the [default list of `PASSWORD_HASHERS`](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-PASSWORD_HASHERS). See also [How Django stores passwords](https://docs.djangoproject.com/en/2.2/topics/auth/passwords/#how-django-stores-passwords) for more information.

### Grant scheme

Access is granted if and only if all of the following is true:

1. The configured API key header is present and correctly formatted. [^3]
2. A usable API key with the prefix of the given key exists in the database. [^4]
3. The hash of the given key matches that of the API key.

[^3]: To customize this behavior, see [API key parsing](guide.md#api-key-parsing).
[^4]: Only unrevoked keys are usable by default, but this can be customized with a [custom manager](guide.md#managers).

## Caveats

[API keys ≠ Security](https://nordicapis.com/why-api-keys-are-not-enough/): depending on your situation, you should probably not use API keys only to authorize your clients.

Besides, it is NOT recommended to use this package for authentication, i.e. retrieving user information from API keys.

Indeed, **using API keys shifts the responsability of Information Security on your clients**. This induces risks, especially if detaining an API key gives access to confidential information or write operations. For example, an attacker could impersonate clients if they let their API keys leak.

As a best practice, you should apply the _Principle of Least Privilege_: allow only those who require resources to access those specific resources. In other words: **if your client needs to access an endpoint, add API permissions on that endpoint only** instead of the whole API.

Besides, it is highly recommended to serve the API over **HTTPS** to ensure the confidentiality of API keys passed in requests.

Act responsibly!
