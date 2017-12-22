from conans import ConanFile, tools
import os, shutil


class TBBConan(ConanFile):
    name = "TBB"
    version = "4.4.4"
    license = "GPLv2 with the (libstdc++) runtime exception"
    url = "https://github.com/memsharded/conan-tbb.git"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        tools.download("https://www.threadingbuildingblocks.org/sites/default/files/software_releases/source/tbb44_20160413oss_src.tgz", "tbb.zip")
        tools.untargz("tbb.zip")
        os.unlink("tbb.zip")
        shutil.move("tbb44_20160413oss", "tbb")
     
    def build(self):
        extra="" if self.options.shared else "extra_inc=big_iron.inc"
        arch="ia32" if self.settings.arch=="x86" else "intel64"
        if self.settings.compiler == "Visual Studio":
            vcvars = tools.vcvars_command(self.settings) 
            self.run("%s && cd tbb && mingw32-make arch=%s %s" % (vcvars, arch, extra))
        else:
            self.run("cd tbb && make arch=%s %s" % (arch, extra)) 

    def package(self):
        self.copy("*.h", "include", "tbb/include")
        build_folder = "tbb/build/"
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        self.copy("*%s*.lib" % build_type, "lib", build_folder, keep_path=False)
        self.copy("*%s*.a" % build_type, "lib", build_folder, keep_path=False) 
        self.copy("*%s*.dll" % build_type, "bin", build_folder, keep_path=False)
        self.copy("*%s*.dylib" % build_type, "lib", build_folder, keep_path=False)
    
        if self.settings.os == "Linux":
            # leaving the below line in case MacOSX build also produces the same bad libs
            extension = "dylib" if self.settings.os == "Macos" else "so"
            if self.options.shared:
                self.copy("*%s*.%s.*" % (build_type, extension), "lib", build_folder, keep_path=False)
                outputlibdir = os.path.join(self.package_folder, "lib")
                os.chdir(outputlibdir)
                for fpath in os.listdir(outputlibdir):
                    self.run("ln -s \"%s\" \"%s\"" % (fpath, fpath[0:fpath.rfind("." + extension)+len(extension)+1]))

    def package_info(self):
        if self.settings.build_type == "Debug":
            self.cpp_info.libs.extend(["tbb_debug", "tbbmalloc_debug"])
            if self.options.shared:
                self.cpp_info.libs.extend(["tbbmalloc_proxy_debug"])
        else:
            self.cpp_info.libs.extend(["tbb", "tbbmalloc"])
            if self.options.shared:
                self.cpp_info.libs.extend(["tbbmalloc_proxy"])

        if not self.options.shared and self.settings.os != "Windows":
            self.cpp_info.libs.extend(["pthread"])
