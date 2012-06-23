# This file is part of PyOP2.
#
# PyOP2 is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PyOP2 is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PyOP2.  If not, see <http://www.gnu.org/licenses>
#
# Copyright (c) 2011, Graham Markall <grm08@doc.ic.ac.uk> and others. Please see
# the AUTHORS file in the main source directory for a full list of copyright
# holders.

"""Example of the PyOP2 API specification. An implementation is pending subject
to the API being finalised."""

from copy import copy

def as_tuple(item, type=None, length=None):
    # Empty list if we get passed None
    if item is None:
        t = []
    else:
        # Convert iterable to list...
        try:
            t = tuple(item)
        # ... or create a list of a single item
        except TypeError:
            t = (item,)*(length or 1)
    if length:
        assert len(t) == length, "Tuple needs to be of length %d" % length
    if type:
        assert all(isinstance(i, type) for i in t), \
                "Items need to be of %s" % type
    return t

# Kernel API

class Access(object):
    """Represents an OP2 access type."""

    _modes = ["READ", "WRITE", "RW", "INC"]

    def __init__(self, mode):
        assert mode in self._modes, "Mode needs to be one of %s" % self._modes
        self._mode = mode

    def __str__(self):
        return "OP2 Access: %s" % self._mode

    def __repr__(self):
        return "Access('%s')" % self._mode

READ  = Access("READ")
WRITE = Access("WRITE")
RW    = Access("RW")
INC   = Access("INC")

class IterationSpace(object):

    def __init__(self, set, dims):
        assert isinstance(set, Set), "set needs to be of type Set"
        self._set = set
        self._dims = as_tuple(dims, int)

    def __str__(self):
        return "OP2 Iteration Space: %s and extra dimensions %s" % (self._set, self._dims)

    def __repr__(self):
        return "IterationSpace(%r, %r)" % (self._set, self._dims)

class Kernel(object):

    def __init__(self, name, code):
        self._name = name
        self._code = code

    def compile():
        pass

    def handle():
        pass

    def __str__(self):
        return "OP2 Kernel: %s" % self._name

    def __repr__(self):
        return 'Kernel("%s", """%s""")' % (self._name, self._code)

# Data API

class Set(object):
    """Represents an OP2 Set."""

    def __init__(self, size, name):
        assert isinstance(size, int), "Size must be of type int"
        assert isinstance(name, str), "Name must be of type str"
        self._size = size
        self._name = name

    def __str__(self):
        return "OP2 Set: %s with size %s" % (self._name, self._size)

    def __repr__(self):
        return "Set(%s, '%s')" % (self._size, self._name)

    def size(self):
        return self._size

class DataCarrier(object):
    """Abstract base class for OP2 data."""

    pass

class Dat(DataCarrier):
    """Represents OP2 vector data. A Dat holds a value for every member of a
    set."""

    _modes = [READ, WRITE, RW, INC]

    def __init__(self, set, dim, datatype, data, name):
        assert isinstance(set, Set), "set must be of type Set"
        assert isinstance(name, str), "Name must be of type str"
        self._set = set
        self._dim = dim
        self._datatype = datatype
        self._data = data
        self._name = name
        self._map = None
        self._access = None

    def __call__(self, map, access):
        assert access in self._modes, \
                "Acess descriptor must be one of %s" % self._modes
        assert map._set == self._set, \
                "Invalid data set for map %s (is %s, should be %s)" \
                % (map._name, map._set._name, self._set._name)
        arg = copy(self)
        arg._map = map
        arg._access = access
        return arg

    def __str__(self):
        call = " associated with (%s) in mode %s" % (self._map, self._access) \
                if self._map and self._access else ""
        return "OP2 Dat: %s on (%s) with dim %s and datatype %s%s" \
               % (self._name, self._set, self._dim, self._datatype, call)

    def __repr__(self):
        call = "(%r, %r)" % (self._map, self._access) \
                if self._map and self._access else ""
        return "Dat(%r, %s, '%s', None, '%s')%s" \
               % (self._set, self._dim, self._datatype, self._name, call)

class Mat(DataCarrier):
    """Represents OP2 matrix data. A Mat is defined on the cartesian product
    of two Sets, and holds an value for each element in the product"""

    _modes = [READ, WRITE, RW, INC]

    def __init__(self, sets, dim, datatype, name):
        assert isinstance(name, str), "Name must be of type str"
        self._sets = as_tuple(sets, Set, 2)
        self._dim = dim
        self._datatype = datatype
        self._name = name
        self._maps = None
        self._access = None

    def __call__(self, maps, access):
        assert access in self._modes, \
                "Acess descriptor must be one of %s" % self._modes
        for map, set in zip(maps, self._sets):
            assert map._set == set, \
                    "Invalid set for map %s (is %s, should be %s)" \
                    % (map._name, map._set._name, set._name)
        arg = copy(self)
        arg._maps = maps
        arg._access = access
        return arg

    def __str__(self):
        call = " associated with (%s, %s) in mode %s" % (self._maps[0], self._maps[1], self._access) \
                if self._maps and self._access else ""
        return "OP2 Mat: %s, row set (%s), col set (%s), dimension %s, datatype %s%s" \
               % (self._name, self._sets[0], self._sets[1], self._dim, self._datatype, call)

    def __repr__(self):
        call = "(%r, %r)" % (self._maps, self._access) \
                if self._maps and self._access else ""
        return "Mat(%r, %s, '%s', '%s')%s" \
               % (self._sets, self._dim, self._datatype, self._name, call)

class Const(DataCarrier):
    """Represents a value that is constant for all elements of all sets."""

    _modes = [READ]

    def __init__(self, dim, datatype, value, name):
        assert isinstance(name, str), "Name must be of type str"
        self._dim = dim
        self._datatype = datatype
        self._value = value
        self._name = name
        self._access = READ

    def __str__(self):
        return "OP2 Const: %s of dim %s and type %s, value %s" \
               % (self._name, self._dim, self._datatype, self._value)

    def __repr__(self):
        return "Const(%s, '%s', %s, '%s')" \
               % (self._dim, self._datatype, self._value, self._name)

class Global(DataCarrier):
    """Represents an OP2 global value."""

    _modes = [READ, INC]

    def __init__(self, name, val=0):
        assert isinstance(name, str), "Name must be of type str"
        self._val = val
        self._name = name
        self._access = None

    def __call__(self, access):
        assert access in self._modes, \
                "Acess descriptor must be one of %s" % self._modes
        arg = copy(self)
        arg._access = access
        return arg

    def __str__(self):
        call = " in mode %s" % self._access if self._access else ""
        return "OP2 Global Argument: %s with value %s%s" \
                % (self._name, self._val, call)

    def __repr__(self):
        call = "(%r)" % self._access if self._access else ""
        return "Global('%s', %s)%s" % (self._name, self._val, call)

    def val(self):
        return self._val

class Map(object):
    """Represents an OP2 map. A map is a relation between two sets."""

    def __init__(self, frm, to, dim, values, name):
        assert isinstance(frm, Set), "From set must be of type Set"
        assert isinstance(to, Set), "To set must be of type Set"
        assert isinstance(name, str), "Name must be of type str"
        self._from = frm
        self._to = to
        self._dim = dim
        self._values = values
        self._name = name
        self._index = None

    def __call__(self, index):
        assert isinstance(index, int), "Only integer indices are allowed"
        return self.indexed(index)

    def indexed(self, index):
        # Check we haven't already been indexed
        assert self._index is None, "Map has already been indexed"
        assert 0 <= index < self._dim, \
                "Index must be in interval [0,%d]" % (self._dim-1)
        indexed = copy(self)
        indexed._index = index
        return indexed

    def __str__(self):
        indexed = " and component %s" % self._index if self._index else ""
        return "OP2 Map: %s from (%s) to (%s) with dim %s%s" \
               % (self._name, self._from, self._to, self._dim, indexed)

    def __repr__(self):
        indexed = "(%s)" % self._index if self._index else ""
        return "Map(%r, %r, %s, None, '%s')%s" \
               % (self._from, self._to, self._dim, self._name, indexed)

# Parallel loop API

class ParLoop(object):
    """Represents an invocation of an OP2 kernel with an access descriptor"""
    def __init__(self, kernel, it_space, *args):
        self._kernel = kernel
        self._it_space = it_space
        self._args = args
