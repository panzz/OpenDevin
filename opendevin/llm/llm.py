import json
from litellm import completion as litellm_completion
from functools import partial

from opendevin import config
from opendevin.logging import llm_prompt_logger, llm_response_logger
from opendevin.logging import opendevin_logger as logger
from agenthub.monologue_agent.utils.tools import num_tokens_from_string

DEFAULT_API_KEY = config.get('LLM_API_KEY')
DEFAULT_BASE_URL = config.get('LLM_BASE_URL')
DEFAULT_MODEL_NAME = config.get('LLM_MODEL')
DEFAULT_LLM_NUM_RETRIES = config.get('LLM_NUM_RETRIES')
DEFAULT_LLM_COOLDOWN_TIME = config.get('LLM_COOLDOWN_TIME')
DEFAULT_LLM_API_VERSION = config.get('LLM_API_VERSION')


class LLM:
    token_cnt = 0
    def __init__(self,
                 model=DEFAULT_MODEL_NAME,
                 api_key=DEFAULT_API_KEY,
                 base_url=DEFAULT_BASE_URL,
                 num_retries=DEFAULT_LLM_NUM_RETRIES,
                 cooldown_time=DEFAULT_LLM_COOLDOWN_TIME,
                 api_version=DEFAULT_LLM_API_VERSION,
                 ):
        self.model_name = model if model else DEFAULT_MODEL_NAME
        self.api_key = api_key if api_key else DEFAULT_API_KEY
        self.base_url = base_url if base_url else DEFAULT_BASE_URL
        self.api_version = api_version if api_version else DEFAULT_LLM_API_VERSION

        self._completion = partial(litellm_completion, model=self.model_name, api_key=self.api_key, base_url=self.base_url, api_version=self.api_version)

        completion_unwrapped = self._completion
        self.token_cnt = 0

        def wrapper(*args, **kwargs):
            if 'messages' in kwargs:
                messages = kwargs['messages']
            else:
                messages = args[1]
            llm_prompt_logger.debug(messages)
            resp = completion_unwrapped(*args, **kwargs)
            message_back = resp['choices'][0]['message']['content']
            self.token_cnt += num_tokens_from_string(json.dumps(messages))
            logger.info(f"LLM Input token count total cost: {self.token_cnt}")
            llm_response_logger.debug(message_back)
            # llm_response_logger.debug(json.dumps(json.loads(message_back), ensure_ascii=False))
            return resp
        self._completion = wrapper  # type: ignore

    @property
    def completion(self):
        """
        Decorator for the litellm completion function.
        """
        return self._completion
