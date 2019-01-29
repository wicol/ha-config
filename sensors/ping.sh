#!/usr/bin/env bash
host=$1
ping -c3 -W2 -w8 $host &> /dev/null 2>&1 && echo ON) || echo OFF
