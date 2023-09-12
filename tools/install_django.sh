#!/bin/sh -ex

PIP="$1"

DJANGO_VERSION=${DJANGO_VERSION:-4.2.5}

exec ${PIP} install django==$DJANGO_VERSION
