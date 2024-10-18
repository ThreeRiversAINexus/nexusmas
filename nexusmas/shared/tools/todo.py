
from shared.tools.shared import NexusTool
from langchain import LLMChain, OpenAI, PromptTemplate

class ToDoMaker(NexusTool):
    def __init__(self):
        self.todo_prompt = PromptTemplate.from_template(
            "You are a planner who is an expert at coming up with a todo list for a given objective. Come up with a todo list for this objective: {objective}"
        )
        self.todo_chain = LLMChain(llm=OpenAI(temperature=0), prompt=self.todo_prompt)
        self.tool_function = "make_todo"
        super().__init__(self.tool_function)

    def make_todo(self, objective: str):
        """
        ALWAYS DO THIS FIRST TO MAKE A PLAN BEFORE PROCEEDING.
        useful for making a plan. Input: an objective to create a todo list for. Output: a todo list for that objective. Please be very clear what the objective is!
        """
        return self.todo_chain.run(objective)


    