# import json
# import re
import time
import datetime
from opendevin.logging import opendevin_logger as logger


def show_exec_time(func):
  """
  Decorator function that measures the execution time of a function.

  Args:
    func (function): The function to be measured.

  Returns:
    function: The wrapped function.
  """
  def wrapper(*args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = int((end_time - start_time)*1000)
    # logger.debug(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} [exec-time] {func.__name__} ran in {execution_time} ms")
    logger.debug(f"[exec-time] {func.__name__} ran in {execution_time} ms")
    return result
  return wrapper

# def is_array_string_in_target(stringArray, targetString):
#   '''
#   Checks if the target string is present in the string array.

#   Args:
#     stringArray (list): The string array to search in.
#     targetString (str): The target string to search for.

#   Returns:
#     bool: True if the target string is found in the string array, False otherwise.
#   '''
#   if not targetString or not len(targetString) or not stringArray or not len(stringArray):
#     return False
#   result = [True for x in stringArray if x.lower() in targetString.lower()]
#   # return result
#   return result[0] if result and len(result) else False

# def parse_chat_completions(contents):
#   '''
#   Parses the contents and concatenates the extracted contents from the choices.

#   Args:
#     contents (str): The contents to be parsed.

#   Returns:
#     str: The concatenated result of the extracted contents.
#   '''
#   result = ""
#   try:
#     if contents.startswith("data: ") and len(contents) > 6:
#       for s in contents.split("\n\n"):
#         s = re.search('data: (.*)}', s)
#         if not s:
#           return result
#         data = json.loads(s.group(1) + '}')
#         choices = data.get('choices', [])
#         for choice in choices:
#           delta = choice.get('delta', {})
#           content = delta.get('content', "")
#           if content and len(content):
#             result += content
#   except Exception as e:
#     print(f"Warning! parse_chat_completions >> ERROR!!! {e}")
#   return result
