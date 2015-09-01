from os import path, environ
import subprocess

def get_package_dir():
    return path.abspath(path.dirname(__file__))


class Compiler(object):
    """A compiler object for creating and loading shared libraries.

    :arg cc: C compiler executable (can be overriden by exporting the
        environment variable ``CC``).
    :arg ld: Linker executable (optional, if ``None``, we assume the compiler
        can build object files and link in a single invocation, can be
        overridden by exporting the environment variable ``LDSHARED``).
    :arg cppargs: A list of arguments to the C compiler (optional).
    :arg ldargs: A list of arguments to the linker (optional)."""
    def __init__(self, cc, ld=None, cppargs=[], ldargs=[]):
        self._cc = environ.get('CC', cc)
        self._ld = environ.get('LDSHARED', ld)
        self._cppargs = cppargs
        self._ldargs = ldargs

    def compile(self, src, out=None, shared=True):
        basename = src.split('.')[0]
        outname = out or "%s.so"%basename if shared else basename
        if shared:
            self._cppargs += ['-fPIC']
            self._ldargs += ['-shared']
        cc = [self._cc] + self._cppargs + ['-o', outname, src] + self._ldargs
        with file('%s.log' % basename, 'w') as logfile:
            logfile.write("Compiling: %s\n" % " ".join(cc))
            try:
                subprocess.check_call(cc, stdout=logfile, stderr=logfile)
            except subprocess.CalledProcessError as e:
                print "Compilation error with:", " ".join(cc)
                print "Log file:", logfile.name
                raise RuntimeError("Error during compilation")
        print "Compiled:", outname
        return outname


class GNUCompiler(Compiler):
    """A compiler object for the GNU Linux toolchain.

    :arg cppargs: A list of arguments to pass to the C compiler
         (optional).
    :arg ldargs: A list of arguments to pass to the linker (optional)."""
    def __init__(self, cppargs=[], ldargs=[]):
        opt_flags = ['-g', '-O3', '-fno-tree-vectorize', '-fopenmp']
        cppargs = ['-Wall', '-std=c++11', '-I%s/include'%get_package_dir()] + opt_flags + cppargs
        ldargs = ['-lopesci', '-Wl,-rpath,%s/lib'%get_package_dir(),
                  '-L%s/lib'%get_package_dir()] + ldargs
        super(GNUCompiler, self).__init__("g++", cppargs=cppargs, ldargs=ldargs)
