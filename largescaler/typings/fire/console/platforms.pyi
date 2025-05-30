"""
This type stub file was generated by pyright.
"""

"""Utilities for determining the current platform and architecture."""
class Error(Exception):
  """Base class for exceptions in the platforms module."""
  ...


class InvalidEnumValue(Error):
  """Exception for when a string could not be parsed to a valid enum value."""
  def __init__(self, given, enum_type, options) -> None:
    """Constructs a new exception.

    Args:
      given: str, The given string that could not be parsed.
      enum_type: str, The human readable name of the enum you were trying to
        parse.
      options: list(str), The valid values for this enum.
    """
    ...
  


class OperatingSystem:
  """An enum representing the operating system you are running on."""
  class _OS:
    """A single operating system."""
    def __init__(self, id, name, file_name) -> None:
      ...
    
    def __str__(self) -> str:
      ...
    
    def __eq__(self, other) -> bool:
      ...
    
    def __hash__(self) -> int:
      ...
    
    def __ne__(self, other) -> bool:
      ...
    
    def __lt__(self, other) -> bool:
      ...
    
    def __gt__(self, other) -> bool:
      ...
    
    def __le__(self, other) -> bool:
      ...
    
    def __ge__(self, other) -> bool:
      ...
    
  
  
  WINDOWS = ...
  MACOSX = ...
  LINUX = ...
  CYGWIN = ...
  MSYS = ...
  _ALL = ...
  @staticmethod
  def AllValues(): # -> list[_OS]:
    """Gets all possible enum values.

    Returns:
      list, All the enum values.
    """
    ...
  
  @staticmethod
  def FromId(os_id, error_on_unknown=...): # -> _OS | None:
    """Gets the enum corresponding to the given operating system id.

    Args:
      os_id: str, The operating system id to parse
      error_on_unknown: bool, True to raise an exception if the id is unknown,
        False to just return None.

    Raises:
      InvalidEnumValue: If the given value cannot be parsed.

    Returns:
      OperatingSystemTuple, One of the OperatingSystem constants or None if the
      input is None.
    """
    ...
  
  @staticmethod
  def Current(): # -> _OS | None:
    """Determines the current operating system.

    Returns:
      OperatingSystemTuple, One of the OperatingSystem constants or None if it
      cannot be determined.
    """
    ...
  
  @staticmethod
  def IsWindows(): # -> bool:
    """Returns True if the current operating system is Windows."""
    ...
  


class Architecture:
  """An enum representing the system architecture you are running on."""
  class _ARCH:
    """A single architecture."""
    def __init__(self, id, name, file_name) -> None:
      ...
    
    def __str__(self) -> str:
      ...
    
    def __eq__(self, other) -> bool:
      ...
    
    def __hash__(self) -> int:
      ...
    
    def __ne__(self, other) -> bool:
      ...
    
    def __lt__(self, other) -> bool:
      ...
    
    def __gt__(self, other) -> bool:
      ...
    
    def __le__(self, other) -> bool:
      ...
    
    def __ge__(self, other) -> bool:
      ...
    
  
  
  x86 = ...
  x86_64 = ...
  ppc = ...
  arm = ...
  _ALL = ...
  _MACHINE_TO_ARCHITECTURE = ...
  @staticmethod
  def AllValues(): # -> list[_ARCH]:
    """Gets all possible enum values.

    Returns:
      list, All the enum values.
    """
    ...
  
  @staticmethod
  def FromId(architecture_id, error_on_unknown=...): # -> _ARCH | None:
    """Gets the enum corresponding to the given architecture id.

    Args:
      architecture_id: str, The architecture id to parse
      error_on_unknown: bool, True to raise an exception if the id is unknown,
        False to just return None.

    Raises:
      InvalidEnumValue: If the given value cannot be parsed.

    Returns:
      ArchitectureTuple, One of the Architecture constants or None if the input
      is None.
    """
    ...
  
  @staticmethod
  def Current(): # -> _ARCH | None:
    """Determines the current system architecture.

    Returns:
      ArchitectureTuple, One of the Architecture constants or None if it cannot
      be determined.
    """
    ...
  


class Platform:
  """Holds an operating system and architecture."""
  def __init__(self, operating_system, architecture) -> None:
    """Constructs a new platform.

    Args:
      operating_system: OperatingSystem, The OS
      architecture: Architecture, The machine architecture.
    """
    ...
  
  def __str__(self) -> str:
    ...
  
  @staticmethod
  def Current(os_override=..., arch_override=...): # -> Platform:
    """Determines the current platform you are running on.

    Args:
      os_override: OperatingSystem, A value to use instead of the current.
      arch_override: Architecture, A value to use instead of the current.

    Returns:
      Platform, The platform tuple of operating system and architecture.  Either
      can be None if it could not be determined.
    """
    ...
  
  def UserAgentFragment(self): # -> str:
    """Generates the fragment of the User-Agent that represents the OS.

    Examples:
      (Linux 3.2.5-gg1236)
      (Windows NT 6.1.7601)
      (Macintosh; PPC Mac OS X 12.4.0)
      (Macintosh; Intel Mac OS X 12.4.0)

    Returns:
      str, The fragment of the User-Agent string.
    """
    ...
  
  def AsyncPopenArgs(self): # -> dict[Any, Any]:
    """Returns the args for spawning an async process using Popen on this OS.

    Make sure the main process does not wait for the new process. On windows
    this means setting the 0x8 creation flag to detach the process.

    Killing a group leader kills the whole group. Setting creation flag 0x200 on
    Windows or running setsid on *nix makes sure the new process is in a new
    session with the new process the group leader. This means it can't be killed
    if the parent is killed.

    Finally, all file descriptors (FD) need to be closed so that waiting for the
    output of the main process does not inadvertently wait for the output of the
    new process, which means waiting for the termination of the new process.
    If the new process wants to write to a file, it can open new FDs.

    Returns:
      {str:}, The args for spawning an async process using Popen on this OS.
    """
    ...
  


class PythonVersion:
  """Class to validate the Python version we are using.

  The Cloud SDK officially supports Python 2.7.

  However, many commands do work with Python 2.6, so we don't error out when
  users are using this (we consider it sometimes "compatible" but not
  "supported").
  """
  MIN_REQUIRED_PY2_VERSION = ...
  MIN_SUPPORTED_PY2_VERSION = ...
  MIN_SUPPORTED_PY3_VERSION = ...
  ENV_VAR_MESSAGE = ...
  def __init__(self, version=...) -> None:
    ...
  
  def SupportedVersionMessage(self, allow_py3): # -> str:
    ...
  
  def IsCompatible(self, allow_py3=..., raise_exception=...): # -> bool:
    """Ensure that the Python version we are using is compatible.

    This will print an error message if not compatible.

    Compatible versions are 2.6 and 2.7 and > 3.4 if allow_py3 is True.
    We don't guarantee support for 2.6 so we want to warn about it.

    Args:
      allow_py3: bool, True if we should allow a Python 3 interpreter to run
        gcloud. If False, this returns an error for Python 3.
      raise_exception: bool, True to raise an exception rather than printing
        the error and exiting.

    Raises:
      Error: If not compatible and raise_exception is True.

    Returns:
      bool, True if the version is valid, False otherwise.
    """
    ...
  


