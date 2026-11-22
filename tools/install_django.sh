#!/bin/sh -ex

PIP="$1"

DJANGO_VERSION=${DJANGO_VERSION:-6.0}

exec ${PIP} install django==$DJANGO_VERSION
