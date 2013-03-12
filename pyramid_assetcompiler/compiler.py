# vim:fileencoding=utf-8:ai:ts=4:sts:et:sw=4:tw=80:
import os, re, glob, shlex, subprocess, hashlib
from pyramid.path import AssetResolver

class Compiler(object):
    """
    Compiler class for the pyramid_assetcompiler add-on.
    """
    def __init__(self, app_settings, path, **kw):
        """
        Initialize the Compiler class.
        
        Required parameters:
        
        :type app_settings: dict
        :param app_settings: The Pyramid application ``settings`` dictionary.
        
        :type path: string
        :param path: The Pyramid ``asset path``.
        
        Optional parameters:
        
        :type compiler: dict or string
        :param compiler: Allows you to either specify a specific compiler to
                         use (e.g. ``coffee``), or assign a brand new
                         compiler dictionary to be used (e.g.
                         ``{'less': {'cmd': 'lessc', 'ext': 'css'}}``)
        
        :type batch: bool
        :param batch: Specify that the class should prepare for a batch
                      compile rather than a normal compile.
        """
        self.settings = app_settings
        self.path = path
        
        self.compilers = self.settings.get('assetcompiler.compilers')
        self.prefix = self.settings.get('assetcompiler.asset_prefix')
        
        if not isinstance(self.compilers, dict):
            raise ValueError('No compilers were found.')
        
        self.compiler = kw.get('compiler', None)
        self.batch = kw.get('batch', False)
        self.hash = None
        self.exists = None
        
        self.fullpath = self.path
        if not os.path.isabs(self.path):
            # Try to resolve the asset full path
            a = AssetResolver()
            self.fullpath = a.resolve(self.path).abspath()
        
        if self.batch:
            if not os.path.isdir(self.fullpath):
                raise EnvironmentError('Directory does not exist: %s' % \
                                       self.fullpath)
        
        else:
            self.filename = os.path.basename(self.fullpath)
            self.dirname = os.path.dirname(self.fullpath)
            self.name = os.path.splitext(self.filename)[0]
            self.ext = os.path.splitext(self.filename)[1][1:]
            
            if self.compiler:
                if not isinstance(self.compiler, dict):
                    self.compiler = self.compilers.get(self.compiler, {})
            else:
                self.compiler = self.compilers.get(self.ext, {})
            
            
            if not self.compiler.get('cmd') or not self.compiler.get('ext'):
                raise ValueError('No compiler found for %s' % self.ext)
    
    
    @property
    def compiled(self):
        """
        Property method to check and see if the initialized asset path has
        already been compiled.
        """
        new_ext = self.compiler['ext']
        
        self.hash = self.hash or self._compute_hash(self.fullpath)
        self.new_filename = '%s%s.%s.%s' % (self.prefix, self.name, self.hash,
                                            new_ext)
        self.new_fullpath = os.path.join(self.dirname, self.new_filename)
        self.new_path = re.sub(r'%s$' % self.filename, self.new_filename,
                                        self.path)
        
        self.exists = self.exists or self._check_exists(self.new_fullpath)
        
        return self.exists
    
    def _check_exists(self, path):
        """
        Convenience method to check if a file already exists.
        """
        if os.path.exists(path):
            return True
        else:
            return False
    
    def _compute_hash(self, path):
        """
        Convenience method to compute the hash key for the compiled asset.
        """
        md5 = hashlib.md5()
        
        # Loop the file, adding chunks to the MD5 generator
        with open(path, 'rb') as f: 
            for chunk in iter(lambda: f.read(128*md5.block_size), b''): 
                md5.update(chunk)
        # Finally, add the mtime
        md5.update(str(os.path.getmtime(path)))
        
        # Get the first 12 characters of the hexdigest
        self.hash = md5.hexdigest()[:12]
        
        return self.hash
    
    def compile(self):
        """
        Runs the compiler for the initialized asset.
        """
        cmd = '%s %s' % (self.compiler['cmd'], self.fullpath)
        
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        
        if proc.returncode != 0 or err:
            raise EnvironmentError('%s\n\n%s' % (err, out))
        else:
            new_dirname = os.path.normpath(os.path.dirname(self.new_fullpath))
            
            if not os.path.exists(new_dirname):
                os.makedirs(new_dirname)
            
            with open(self.new_fullpath, 'w') as f:
                f.write(out)
            
            return self.new_path
    
    def batch_compile(self):
        """
        Runs the compiler for the initialized batch of assets.
        """
        for ext, data in list(self.compilers.items()):
            for asset in glob.glob(os.path.join(self.fullpath, '*.%s' % ext)):
                filename = os.path.basename(asset)
                dirname = os.path.dirname(asset)
                name = os.path.splitext(filename)[0]
                new_ext = data['ext']
                
                self.hash = self.hash or self._compute_hash(asset)
                new_filename = '%s%s.%s.%s' % (self.prefix, name, self.hash,
                                               new_ext)
                new_fullpath = os.path.join(dirname, new_filename)
                
                if not os.path.exists(new_fullpath):
                    cmd = '%s %s' % (data['cmd'], asset)
                    
                    proc = subprocess.Popen(
                        shlex.split(cmd),
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    out, err = proc.communicate()
                    
                    if proc.returncode != 0 or err:
                        raise EnvironmentError('%s\n\n%s' % (err, out))
                    else:
                        new_dirname = os.path.normpath(
                            os.path.dirname(new_fullpath)
                        )
                        
                        if not os.path.exists(new_dirname):
                            os.makedirs(new_dirname)
                        
                        with open(new_fullpath, 'w') as f:
                            f.write(out)
    
    def compiled_data(self):
        if not self.exists:
            raise ValueError('Source not found. Has it been compiled?')
        
        with open(self.new_fullpath) as f:
            data = f.read()
        
        return data
