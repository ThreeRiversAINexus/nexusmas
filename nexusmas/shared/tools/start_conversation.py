from langchain.tools import Tool
class {{ class_name }}():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def {{ function_name }}(self, *args):
        {{ function_implementation }}

    def tool_factory(self):
        return [Tool(
            name="{{ tool_name }}",
            func=self.{{ function_name }},
            description="""
            accepts a full path to a directory of PDFs
            used for {{ tool_description }}
            """
        )]
