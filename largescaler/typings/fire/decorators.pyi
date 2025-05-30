"""
This type stub file was generated by pyright.
"""

from typing import Any, Dict

"""These decorators provide function metadata to Python Fire.

SetParseFn and SetParseFns allow you to set the functions Fire uses for parsing
command line arguments to client code.
"""
FIRE_METADATA = ...
FIRE_PARSE_FNS = ...
ACCEPTS_POSITIONAL_ARGS = ...
def SetParseFn(fn, *arguments): # -> Callable[..., Any]:
  """Sets the fn for Fire to use to parse args when calling the decorated fn.

  Args:
    fn: The function to be used for parsing arguments.
    *arguments: The arguments for which to use the parse fn. If none are listed,
      then this will set the default parse function.
  Returns:
    The decorated function, which now has metadata telling Fire how to perform.
  """
  ...

def SetParseFns(*positional, **named): # -> Callable[..., Any]:
  """Set the fns for Fire to use to parse args when calling the decorated fn.

  Returns a decorator, which when applied to a function adds metadata to the
  function telling Fire how to turn string command line arguments into proper
  Python arguments with which to call the function.

  A parse function should accept a single string argument and return a value to
  be used in its place when calling the decorated function.

  Args:
    *positional: The functions to be used for parsing positional arguments.
    **named: The functions to be used for parsing named arguments.
  Returns:
    The decorated function, which now has metadata telling Fire how to perform.
  """
  ...

def GetMetadata(fn) -> Dict[str, Any]:
  """Gets metadata attached to the function `fn` as an attribute.

  Args:
    fn: The function from which to retrieve the function metadata.
  Returns:
    A dictionary mapping property strings to their value.
  """
  ...

def GetParseFns(fn) -> Dict[str, Any]:
  ...

