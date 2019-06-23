# Security

## Key generation scheme

An API key is composed of two items:

- A prefix `P`, which is a generated string of 8 characters.
- A secret key `SK`, which is a generated string of 32 characters.

The generated key that clients use to [make authorized requests](#making-authorized-requests) is `GK = P.SK`. It is treated with the same level of care than passwords:

- Only a hashed version is stored in the database. The hash is computed using the default password hasher\* (see also [How Django stores passwords](https://docs.djangoproject.com/en/2.1/topics/auth/passwords/#how-django-stores-passwords)).
- The generated key is shown only once to the client upon API key creation.

\*All hashers provided by Django should be supported. `djangorestframework-api-key` is tested against the [default list of `PASSWORD_HASHERS`](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-PASSWORD_HASHERS).

## Grant scheme

Access is granted if and only if all of the following is true:

1. The API key header is present and correctly formatted (see [Making authorized requests](#making-authorized-requests)).
2. An unrevoked API key with the prefix of the given key exists in the database.
3. The hash of the given key matches that of the API key.

## Caveats

[API keys ≠ Security](https://nordicapis.com/why-api-keys-are-not-enough/): depending on your situation, you should probably not rely on API keys only to authenticate/authorize your clients.

**Using API keys shifts the responsability of Information Security on your clients**. This induces risks, especially if detaining an API key gives access to confidential information or write operations. For example, an attacker could impersonate clients if they let their API keys leak.

As a best practice, you should apply the _Principle of Least Privilege_: allow only those who require resources to access those specific resources. In other words: **if your client needs to access an endpoint, add API permissions on that endpoint only** instead of the whole API.

Besides, it is highly recommended to serve the API over **HTTPS** to ensure the confidentiality of API keys passed in requests.

Act responsibly!
