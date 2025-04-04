#!/bin/sh -ex

PIP="$1"

DJANGO_VERSION=${DJANGO_VERSION:-5.2}

exec ${PIP} install django==$DJANGO_VERSION
