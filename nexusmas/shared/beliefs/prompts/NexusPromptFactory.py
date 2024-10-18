from shared.beliefs.prompts.NexusPrompt import NexusPrompt, NexusSimplePrompt
import datetime
class NexusPromptFactory():
    def __init__(self, *args, **kwargs):
        # do something
        pass

    def get_current_time(self):
        return datetime.datetime.now().strftime('Current date: %Y-%m-%d\nCurrent time: %H:%M:%S')

    def create_simple_prompt(self, memory_variable=None, point=None, *args, **kwargs):
        np = NexusSimplePrompt(
            point=point,
            **kwargs
        )
        return np.get_simple_prompt(memory_variable=memory_variable)

    def create_chat_prompt(self, *args, **kwargs):
        np = NexusPrompt(
            **kwargs
        )
        return np.get_chat_prompt_template_object()
    
    def create_prompt(self, *args, **kwargs):
        np = NexusPrompt(
            **kwargs
        )
        return np.get_prompt_template_object()