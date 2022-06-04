#!/bin/sh -ex

PIP="$1"

DJANGO_VERSION=${DJANGO_VERSION:-4.0.5}

exec ${PIP} install django[argon2,bcrypt]==$DJANGO_VERSION
