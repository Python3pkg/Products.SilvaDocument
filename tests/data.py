# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import os

def testopen(path, rw='r'):
    directory = os.path.dirname(__file__)
    return open(os.path.join(directory, 'data', path), rw)
