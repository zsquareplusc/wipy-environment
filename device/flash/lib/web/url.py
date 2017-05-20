#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause


def decode(b_url):  # expecting bytes
    parts = b_url.split(b'%')
    d = bytearray(parts[0])  # the 1st is special
    for part in parts[1:]:
        if part:
            d.append(int(part[:2], 16))
            d.extend(part[2:])
    return bytes(d).decode('utf-8')
