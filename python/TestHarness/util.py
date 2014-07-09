import os, re
from subprocess import *
from time import strftime, gmtime, ctime, localtime, asctime

TERM_COLS = 110

LIBMESH_OPTIONS = {
  'mesh_mode' :    { 're_option' : r'#define\s+LIBMESH_ENABLE_PARMESH\s+(\d+)',
                     'default'   : 'SERIAL',
                     'options'   :
                       {
      'PARALLEL' : '1',
      'SERIAL'   : '0'
      }
                     },
  'unique_ids' :   { 're_option' : r'#define\s+LIBMESH_ENABLE_UNIQUE_ID\s+(\d+)',
                     'default'   : 'FALSE',
                     'options'   :
                       {
      'TRUE'  : '1',
      'FALSE' : '0'
      }
                     },
  'dtk' :          { 're_option' : r'#define\s+LIBMESH_HAVE_DTK\s+(\d+)',
                     'default'   : 'FALSE',
                     'options'   :
                       {
      'TRUE'  : '1',
      'FALSE' : '0'
      }
                     },
  'vtk' :          { 're_option' : r'#define\s+LIBMESH_HAVE_VTK\s+(\d+)',
                     'default'   : 'FALSE',
                     'options'   :
                       {
      'TRUE'  : '1',
      'FALSE' : '0'
      }
                     },
  'tecplot' :      { 're_option' : r'#define\s+LIBMESH_HAVE_TECPLOT_API\s+(\d+)',
                     'default'   : 'FALSE',
                     'options'   :
                       {
      'TRUE'  : '1',
      'FALSE' : '0'
      }
                     },
  'petsc_major' :  { 're_option' : r'#define\s+LIBMESH_DETECTED_PETSC_VERSION_MAJOR\s+(\d+)',
                     'default'   : '1'
                   },
  'petsc_minor' :  { 're_option' : r'#define\s+LIBMESH_DETECTED_PETSC_VERSION_MINOR\s+(\d+)',
                     'default'   : '1'
                   },
}


## Run a command and return the output, or ERROR: + output if retcode != 0
def runCommand(cmd):
  p = Popen([cmd],stdout=PIPE,stderr=STDOUT, close_fds=True, shell=True)
  output = p.communicate()[0]
  if (p.returncode != 0):
    output = 'ERROR: ' + output
  return output

## print an optionally colorified test result
#
# The test will not be colored if
# 1) options.colored is False,
# 2) the environment variable BITTEN_NOCOLOR is true, or
# 3) the color parameter is False.
def printResult(test_name, result, timing, start, end, options, color=True):
  f_result = ''

  cnt = (TERM_COLS-2) - len(test_name + result)
  if color:
    any_match = False
    # Color leading paths
    m = re.search(r'(.*):(.*)', test_name)
    if m:
      test_name = colorText(m.group(1), options, 'CYAN') + ':' + m.group(2)
    # Color the Caveats CYAN
    m = re.search(r'(\[.*?\])', result)
    if m:
      any_match = True
      f_result += colorText(m.group(1), options, 'CYAN') + " "
    # Color Exodiff or CVSdiff tests YELLOW
    m = re.search('(FAILED \((?:EXODIFF|CSVDIFF)\))', result)
    if m:
      any_match = True
      f_result += colorText(m.group(1), options, 'YELLOW')
    else:
      # Color remaining FAILED tests RED
      m = re.search('(FAILED \(.*\))', result)
      if m:
        any_match = True
        f_result += colorText(m.group(1), options, 'RED')
    # Color deleted tests RED
    m = re.search('(deleted) (\(.*\))', result)
    if m:
      any_match = True
      f_result += colorText(m.group(1), options, 'RED') + ' ' + m.group(2)
    # Color long running tests YELLOW
    m = re.search('(RUNNING\.\.\.)', result)
    if m:
      any_match = True
      f_result += colorText(m.group(1), options, 'YELLOW')
    # Color PBS status CYAN
    m = re.search('((?:LAUNCHED|RUNNING(?!\.)|EXITING|QUEUED))', result)
    if m:
      any_match = True
      f_result += colorText(m.group(1), options, 'CYAN')
    # Color Passed tests GREEN
    m = re.search('(OK)', result)
    if m:
      any_match = True
      f_result += colorText(m.group(1), options, 'GREEN')

    if not any_match:
      f_result = result

    f_result = test_name + '.'*cnt + ' ' + f_result
  else:
    f_result = test_name + '.'*cnt + ' ' + result

  # Tack on the timing if it exists
  if timing:
    f_result += ' [' + '%0.3f' % float(timing) + 's]'
  if options.debug_harness:
    f_result += ' Start: ' + '%0.3f' % start + ' End: ' + '%0.3f' % end
  return f_result

## Color the error messages if the options permit, also do not color in bitten scripts because
# it messes up the trac output.
# supports weirded html for more advanced coloring schemes. \verbatim<r>,<g>,<y>,<b>\endverbatim All colors are bolded.

def colorText(str, options, color, html=False):
  # ANSI color codes for colored terminal output
  color_codes = {'RESET':'\033[0m','BOLD':'\033[1m','RED':'\033[31m','GREEN':'\033[35m','CYAN':'\033[34m','YELLOW':'\033[33m','MAGENTA':'\033[32m'}
  if options.code:
    color_codes['GREEN'] = '\033[32m'
    color_codes['CYAN']  = '\033[36m'
    color_codes['MAGENTA'] = '\033[35m'

  if options.colored and not (os.environ.has_key('BITTEN_NOCOLOR') and os.environ['BITTEN_NOCOLOR'] == 'true'):
    if html:
      str = str.replace('<r>', color_codes['BOLD']+color_codes['RED'])
      str = str.replace('<c>', color_codes['BOLD']+color_codes['CYAN'])
      str = str.replace('<g>', color_codes['BOLD']+color_codes['GREEN'])
      str = str.replace('<y>', color_codes['BOLD']+color_codes['YELLOW'])
      str = str.replace('<b>', color_codes['BOLD'])
      str = re.sub(r'</[rcgyb]>', color_codes['RESET'], str)
    else:
      str = color_codes[color] + str + color_codes['RESET']
  elif html:
    str = re.sub(r'</?[rcgyb]>', '', str)    # strip all "html" tags

  return str

def getPlatforms():
  # We'll use uname to figure this out
  # Supported platforms are LINUX, DARWIN, SL, LION or ALL
  platforms = set()
  platforms.add('ALL')
  raw_uname = os.uname()
  if raw_uname[0].upper() == 'DARWIN':
    platforms.add('DARWIN')
    if re.match("10\.", raw_uname[2]):
      platforms.add('SL')
    if re.match("11\.", raw_uname[2]):
      platforms.add("LION")
  else:
    platforms.add(raw_uname[0].upper())
  return platforms

def getCompilers(libmesh_dir):
  # We'll use the GXX-VERSION string from LIBMESH's Make.common
  # to figure this out
  # Supported compilers are GCC, INTEL or ALL
  compilers = set()
  compilers.add('ALL')

  # Get the gxx compiler.  Note that the libmesh-config script
  # can live in different places depending on whether libmesh is
  # "installed" or not.

  # Installed location of libmesh-config script
  libmesh_config_installed   = libmesh_dir + '/bin/libmesh-config'

  # Uninstalled location of libmesh-config script
  libmesh_config_uninstalled = libmesh_dir + '/contrib/bin/libmesh-config'

  # The eventual variable we will use to refer to libmesh's configure script
  libmesh_config = ''

  if os.path.exists(libmesh_config_installed):
    libmesh_config = libmesh_config_installed

  elif os.path.exists(libmesh_config_uninstalled):
    libmesh_config = libmesh_config_uninstalled

  else:
    print "Error! Could not find libmesh's config script in any of the usual locations!"
    exit(1)

  # Pass the --cxx option to the libmesh-config script, and check the result
  command = libmesh_config + ' --cxx'
  p = Popen(command, shell=True, stdout=PIPE)
  mpicxx_cmd = p.communicate()[0].strip()

  # Account for useage of distcc
  if "distcc" in mpicxx_cmd:
    split_cmd = mpicxx_cmd.split()
    mpicxx_cmd = split_cmd[-1]

  # If mpi ic on the command, run -show to get the compiler
  if "mpi" in mpicxx_cmd:
    p = Popen(mpicxx_cmd + " -show", shell=True, stdout=PIPE)
    raw_compiler = p.communicate()[0]
  else:
    raw_compiler = mpicxx_cmd

  if re.match('icpc', raw_compiler) != None:
    compilers.add("INTEL")
  elif re.match('[cg]\+\+', raw_compiler) != None:
    compilers.add("GCC")
  elif re.match('clang\+\+', raw_compiler) != None:
    compilers.add("CLANG")

  return compilers

def getPetscVersion(libmesh_dir):
  major_version = getLibMeshConfigOption(libmesh_dir, 'petsc_major')
  minor_version = getLibMeshConfigOption(libmesh_dir, 'petsc_minor')
  if len(major_version) != 1 or len(minor_version) != 1:
    print "Error determining PETSC version"
    exit(1)

  return major_version.pop() + '.' + minor_version.pop()

# Break down petsc version logic in a new define
# TODO: find a way to eval() logic instead
def checkPetscVersion(checks, test):
  # If any version of petsc works, return true immediately
  if 'ALL' in set(test['petsc_version']):
    return (True, None, None)
  # Iterate through petsc versions in test[PETSC_VERSION] and match it against check[PETSC_VERSION]
  for petsc_version in test['petsc_version']:
    logic, version = re.search(r'(.*?)(\d\S+)', petsc_version).groups()
    # Exact match
    if logic == '' or logic == '=':
      if version == checks['petsc_version']:
        return (True, None, version)
      else:
        return (False, '!=', version)
    # Logical match
    if logic == '>' and checks['petsc_version'][0:3] > version[0:3]:
      return (True, None, version)
    elif logic == '>=' and checks['petsc_version'][0:3] >= version[0:3]:
      return (True, None, version)
    elif logic == '<' and checks['petsc_version'][0:3] < version[0:3]:
      return (True, None, version)
    elif logic == '<=' and checks['petsc_version'][0:3] <= version[0:3]:
      return (True, None, version)
  return (False, logic, version)


def getLibMeshConfigOption(libmesh_dir, option):
  # Some tests work differently with parallel mesh enabled
  # We need to detect this condition
  option_set = set()
  option_set.add('ALL')

  filenames = [
    libmesh_dir + '/include/base/libmesh_config.h',   # Old location
    libmesh_dir + '/include/libmesh/libmesh_config.h' # New location
    ];

  success = 0
  for filename in filenames:
    if success == 1:
      break

    try:
      f = open(filename)
      contents = f.read()
      f.close()

      info = LIBMESH_OPTIONS[option]
      m = re.search(info['re_option'], contents)
      if m != None:
        if 'options' in info:
          for value, option in info['options'].iteritems():
            if m.group(1) == option:
              option_set.add(value)
        else:
          option_set.clear()
          option_set.add(m.group(1))
      else:
        option_set.add(info['default'])

      success = 1

    except IOError, e:
      # print "Warning: I/O Error trying to read", filename, ":", e.strerror, "... Will try other locations."
      pass

  if success == 0:
    print "Error! Could not find libmesh_config.h in any of the usual locations!"
    exit(1)

  return option_set

def getSharedOption(libmesh_dir):
  # Some tests may only run properly with shared libraries on/off
  # We need to detect this condition
  shared_option = set()
  shared_option.add('ALL')

  # MOOSE no longer relies on Make.common being present.  This gives us the
  # potential to work with "uninstalled" libmesh trees, for example.

  # Installed location of libmesh libtool script
  libmesh_libtool_installed   = libmesh_dir + '/contrib/bin/libtool'

  # Uninstalled location of libmesh libtool script
  libmesh_libtool_uninstalled = libmesh_dir + '/libtool'

  # The eventual variable we will use to refer to libmesh's libtool script
  libmesh_libtool = ''

  if os.path.exists(libmesh_libtool_installed):
    libmesh_libtool = libmesh_libtool_installed

  elif os.path.exists(libmesh_libtool_uninstalled):
    libmesh_libtool = libmesh_libtool_uninstalled

  else:
    print "Error! Could not find libmesh's libtool script in any of the usual locations!"
    exit(1)

  # Now run the libtool script (in the shell) to see if shared libraries were built
  command = libmesh_libtool + " --config | grep build_libtool_libs | cut -d'=' -f2"

  # Note: the strip() command removes the trailing newline
  p = Popen(command, shell=True, stdout=PIPE)
  result = p.communicate()[0].strip()

  if re.search('yes', result) != None:
    shared_option.add('DYNAMIC')
  elif re.search('no', result) != None:
    shared_option.add('STATIC')
  else:
    # Neither no nor yes?  Not possible!
    print "Error! Could not determine whether shared libraries were built."
    exit(1)

  return shared_option
