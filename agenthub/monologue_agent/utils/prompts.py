from typing import List

from . import json

from opendevin.action import (
    action_from_dict,
    Action,
)
from opendevin.observation import (
    CmdOutputObservation,
)

ACTION_PROMPT_OLD = """
You're a thoughtful robot. Your main task is this:

%(task)s

Don't expand the scope of your task--just complete it as written.

This is your internal monologue, in JSON format:

%(monologue)s


Your most recent thought is at the bottom of that monologue. Continue your train of thought.
What is your next thought or action? Your response must be in JSON format.
It must be an object, and it must contain two fields:
* `action`, which is one of the actions below
* `args`, which is a map of key-value pairs, specifying the arguments for that action

Here are the possible actions:
* `read` - reads the content of a file. Arguments:
  * `path` - the path of the file to read
* `write` - writes the content to a file. Arguments:
  * `path` - the path of the file to write
  * `content` - the content to write to the file
* `run` - runs a command. Arguments:
  * `command` - the command to run
  * `background` - if true, run the command in the background, so that other commands can be run concurrently. Useful for e.g. starting a server. You won't be able to see the logs. You don't need to end the command with `&`, just set this to true.
* `kill` - kills a background command
  * `id` - the ID of the background command to kill
* `browse` - opens a web page. Arguments:
  * `url` - the URL to open
* `recall` - recalls a past memory. Arguments:
  * `query` - the query to search for
* `think` - make a plan, set a goal, or record your thoughts. Arguments:
  * `thought` - the thought to record
* `finish` - if you're absolutely certain that you've completed your task and have tested your work, use the finish action to stop working.

%(background_commands)s

You MUST take time to think in between read, write, run, browse, and recall actions.
You should never act twice in a row without thinking. But if your last several
actions are all "think" actions, you should consider taking a different action.

Notes:
* your environment is Debian Linux. You can install software with `apt`
* your working directory will not change, even if you run `cd`. All commands will be run in the `/workspace` directory.
* don't run interactive commands, or commands that don't return (e.g. `node server.js`). You may run commands in the background (e.g. `node server.js &`)

What is your next thought or action? Again, you must reply with JSON, and only with JSON.

%(hint)s
"""

ACTION_PROMPT = """
你是一个有思想的机器人。 你的主要任务是这样的：

%(task)s

不要扩大你的任务范围——只需按照书面规定完成即可。

这是你的内心独白，JSON 格式：

%(monologue)s


你最近的想法就在这段独白的底部。 继续你的思路。
您下一步的想法或行动是什么？ 您的响应必须采用 JSON 格式。
它必须是一个对象，并且必须包含两个字段：
* `action`, 这是以下操作之一
* `args`,这是键值对的映射，指定该操作的参数

以下是可能的操作：
* `read` - 读取文件的内容。 Arguments:
  * `path` - 要读取的文件的路径
* `write` - 将内容写入文件。 Arguments:
  * `path` - 要写入的文件的路径
  * `content` - 要写入文件的内容
* `run` - 运行命令。Arguments:
  * `command` - 要运行的命令
  * `background` - 如果为 true，则在后台运行该命令，以便其他命令可以同时运行。 对于例如有用 启动服务器。 您将无法看到日志。 您不需要以“&”结束命令，只需将其设置为 true 即可。
* `kill` - 杀死后台命令
  * `id` - 要杀死的后台命令的ID
* `browse` - 打开网页。 Arguments:
  * `url` - 要打开的 URL
* `recall` - 回忆过去的记忆。Arguments:
  * `query` - 要搜索的查询
* `think` - 制定计划、设定目标或记录您的想法。 Arguments:
  * `thought` - 要记录的想法
* `finish` - 如果您绝对确定已完成任务并测试了您的工作，请使用finish action来停止工作。

%(background_commands)s

您必须花时间在读取、写入、运行、浏览和调用操作之间进行思考。
你不应该不假思索地连续两次行动。 但如果你最后几个
行动都是“思考”行动，你应该考虑采取不同的行动。

注意:
* 您的环境是 Debian Linux。 您可以使用`apt`安装软件
* 即使你运行 `cd`，你的工作目录也不会改变。 所有命令都将在“/workspace”目录中运行。
* 不要运行交互式命令或不返回的命令（例如“node server.js”）。 您可以在后台运行命令（例如“node server.js &”）

您下一步的想法或行动是什么？ 最后，您必须使用 JSON 进行回复，并且只能使用 JSON。

%(hint)s
"""


MONOLOGUE_SUMMARY_PROMPT_OLD = """
Below is the internal monologue of an automated LLM agent. Each
thought is an item in a JSON array. The thoughts may be memories,
actions taken by the agent, or outputs from those actions.
Please return a new, smaller JSON array, which summarizes the
internal monologue. You can summarize individual thoughts, and
you can condense related thoughts together with a description
of their content.

%(monologue)s

Make the summaries as pithy and informative as possible.
Be specific about what happened and what was learned. The summary
will be used as keywords for searching for the original memory.
Be sure to preserve any key words or important information.

Your response must be in JSON format. It must be an object with the
key `new_monologue`, which is a JSON array containing the summarized monologue.
Each entry in the array must have an `action` key, and an `args` key.
The action key may be `summarize`, and `args.summary` should contain the summary.
You can also use the same action and args from the source monologue.
"""

MONOLOGUE_SUMMARY_PROMPT = """
以下是自动化LLM agent的内心独白。每个
thought 都是 JSON 数组中的一项。The thoughts 可能是记忆,
actions taken by the agent, 或者从这些actions里输出.
请返回一个新的、更小的 JSON 数组，其中总结了内心独白。 可以总结一下个人的想法，
你可以将相关的想法与描述与他们的内容结合起来。

%(monologue)s

你要确保摘要尽可能简洁且内容丰富。
你要具体说明发生了什么以及从中学到了什么。摘要将用作搜索原始记忆的关键字。请务必保留所有关键词或重要信息。

您的回复必须采用 JSON 格式。它必须是一个包含带有key值 `new_monologue`的对象，同时它也是一个包含摘要独白的 JSON 数组。
数组中的每个条目都必须有一个`action` key和一个`args` key。
The action key可以是`summarize`，并且`args.summary`应包含摘要。
您还可以使用源独白中的相同action和参数。
"""


def get_summarize_monologue_prompt(thoughts: List[dict]):
    """
    Gets the prompt for summarizing the monologue

    Returns: 
    - str: A formatted string with the current monologue within the prompt
    """
    return MONOLOGUE_SUMMARY_PROMPT % {
        'monologue': json.dumps({'old_monologue': thoughts}, indent=2),
    }

def get_request_action_prompt(
        task: str,
        thoughts: List[dict],
        background_commands_obs: List[CmdOutputObservation] = [],
):
    """
    Gets the action prompt formatted with appropriate values.

    Parameters:
    - task (str): The current task the agent is trying to accomplish
    - thoughts (List[dict]): The agent's current thoughts
    - background_commands_obs (List[CmdOutputObservation]): List of all observed background commands running

    Returns:
    - str: Formatted prompt string with hint, task, monologue, and background included
    """

    hint = ''
    if len(thoughts) > 0:
        latest_thought = thoughts[-1]
        if "action" in latest_thought:
            if latest_thought["action"] == 'think':
                # if latest_thought["args"]['thought'].startswith("OK so my task is"):
                if latest_thought["args"]['thought'].startswith("好的，所以我的任务是"):
                    # hint = "You're just getting started! What should you do first?"
                    hint = "你才刚刚开始！ 你应该先做什么？"
                else:
                    #  hint = "You've been thinking a lot lately. Maybe it's time to take action?"
                    hint = "你最近想了很多。 也许是时候take action?"
            elif latest_thought["action"] == 'error':
                # hint = "Looks like that last command failed. Maybe you need to fix it, or try something else."
                hint = "看起来最后一个命令失败了。 也许您需要修复它，或者尝试其他方法。"

    bg_commands_message = ""
    if len(background_commands_obs) > 0:
        # bg_commands_message = "The following commands are running in the background:"
        bg_commands_message = "以下命令在后台运行："
        for command_obs in background_commands_obs:
            bg_commands_message += f"\n`{command_obs.command_id}`: {command_obs.command}"
        # bg_commands_message += "\nYou can end any process by sending a `kill` action with the numerical `id` above."
        bg_commands_message += "\n您可以通过发送带有上面数字“id”的“kill”操作来结束任何进程。"
        
    return ACTION_PROMPT % {
        'task': task,
        'monologue': json.dumps(thoughts, indent=2),
        'background_commands': bg_commands_message,
        'hint': hint,
    }

def parse_action_response(response: str) -> Action:
    """
    Parses a string to find an action within it

    Parameters:
    - response (str): The string to be parsed

    Returns:
    - Action: The action that was found in the response string
    """
    action_dict = json.loads(response)
    if 'content' in action_dict:
        # The LLM gets confused here. Might as well be robust
        action_dict['contents'] = action_dict.pop('content')
    return action_from_dict(action_dict)

def parse_summary_response(response: str) -> List[dict]:
    """
    Parses a summary of the monologue

    Parameters:
    - response (str): The response string to be parsed

    Returns:
    - List[dict]: The list of summaries output by the model
    """
    parsed = json.loads(response)
    return parsed['new_monologue']
