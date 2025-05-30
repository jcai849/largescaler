"""
This type stub file was generated by pyright.
"""

"""Simple console pager."""
class Pager:
  """A simple console text pager.

  This pager requires the entire contents to be available. The contents are
  written one page of lines at a time. The prompt is written after each page of
  lines. A one character response is expected. See HELP_TEXT below for more
  info.

  The contents are written as is. For example, ANSI control codes will be in
  effect. This is different from pagers like more(1) which is ANSI control code
  agnostic and miscalculates line lengths, and less(1) which displays control
  character names by default.

  Attributes:
    _attr: The current ConsoleAttr handle.
    _clear: A string that clears the prompt when written to _out.
    _contents: The entire contents of the text lines to page.
    _height: The terminal height in characters.
    _out: The output stream, log.out (effectively) if None.
    _prompt: The page break prompt.
    _search_direction: The search direction command, n:forward, N:reverse.
    _search_pattern: The current forward/reverse search compiled RE.
    _width: The termonal width in characters.
  """
  HELP_TEXT = ...
  PREV_POS_NXT_REPRINT = ...
  def __init__(self, contents, out=..., prompt=...) -> None:
    """Constructor.

    Args:
      contents: The entire contents of the text lines to page.
      out: The output stream, log.out (effectively) if None.
      prompt: The page break prompt, a default prompt is used if None..
    """
    ...
  
  def Run(self): # -> None:
    """Run the pager."""
    ...
  


