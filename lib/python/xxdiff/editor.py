#!/usr/bin/env python
# This file is part of the xxdiff package.  See xxdiff for license and details.

"""
Functions for spawning editor windows.
"""

__author__ = "Martin Blais <blais@furius.ca>"


# stdlib imports.
import sys, os, optparse, tempfile
from os.path import *
from subprocess import Popen, PIPE
import shutil

# xxdiff imports.
import xxdiff.invoke
from xxdiff.scripts import tmpprefix


__all__ = ('spawn_editor',)


#-------------------------------------------------------------------------------
#
def_editor = ["xterm", "-e", '/usr/bin/vi "%s"']

#-------------------------------------------------------------------------------
#
def spawn_editor( initcontents=None, filename=None ):
    """
    Spawns an editor window and returns a waitable object that will block until
    the editor is done and recuperate the text once it's done.  If you delete
    the returned object without waiting on it, the editor program is killed.
    
    If 'initcontents' is given, it is inserted in the temporary file to be
    edited before spawing the editor.  If 'filename' is specified, the editor is
    spawned on that file rather than a temporary.

    This function returns the contents of the edited file, or None, if the edit
    was cancelled.  It may return an empty string.
    """
    # Create and the filename that we will eventually read from.
    tmpf = None
    if filename is not None:
        tmpf = open(filename, 'w+')
    else:
        tmpf = tempfile.NamedTemporaryFile('w+', prefix=tmpprefix)
        filename = tmpf.name
        
    # Initialize the contents of the file if requested.
    if initcontents is not None:
        assert isinstance(initcontents, str)
        tmpf.write(initcontents)
        tmpf.flush()

    # Compute the command to spawn to launch the editor.
    #
    # Note: the editor should the kind to open a new window because we're going
    # to keep printing stuff to stdout during the diffing.  You can just set it
    # up to spawn a new VT if you need to, like in an xterm or something.
    for var in 'XXDIFF_EDITOR', 'SVN_EDITOR', 'VISUAL', 'EDITOR':
        editor = os.environ.get(var, None)
        if editor:
            break

    if editor:
        if '%s' in editor:
            editor %= filename
            cmd = editor
        else:
            cmd = [editor, filename]
    else:
        cmd = def_editor
        cmd[-1] %= filename

    p = Popen(cmd, shell=bool(editor), stdout=PIPE, stderr=PIPE)
    
    def waiter():
        "Waiter closure."
        stdout, stderr = p.communicate()
        if stderr:
            raise RuntimeError("Error running editor:\n%s\n" % stderr)
        tmpf.seek(0)
        return tmpf.read()
        
    return waiter

