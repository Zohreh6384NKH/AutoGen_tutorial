import tempfile
import os
from autogen import GroupChatManager
from autogen import GroupChat
from autogen import ConversableAgent



temp_dir = tempfile.gettempdir()

arithmetic_agent = ConversableAgent(
    "arithmetic_agent",
    llm_config=False,
    human_input_mode="ALWAYS",                # Never ask for human input.
    code_execution_config={"work_dir": temp_dir, "use_docker": False}
    
)


code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message = "you are a code writer agent. you write python script in mark down blocks.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  # Never ask for human input.
    
)


poetry_agent = ConversableAgent(
    "poetry_agent",
    system_message = "you are an AI poet. ",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
    human_input_mode="NEVER",  # Never ask for human input.
)
# Create a group chat with introductions enabled
group_chat_with_intros = GroupChat(
    agents=[arithmetic_agent, code_writer_agent, poetry_agent],  # Add any agents you want to the group chat
    messages=[],  # Start with an empty message history
    max_round=6,  # Maximum rounds of conversation
    send_introductions=True,  # Enable agent introductions
)

# Create the GroupChatManager for the group chat
group_chat_manager_with_intros = GroupChatManager(
    groupchat=group_chat_with_intros,
    llm_config={"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]},
)

#define nested chats using sequential chat patterns

nested_chats = [
    {
        "recipient": group_chat_manager_with_intros,
        "summary_method": "reflection_with_llm",
        "summary_prompt": "Summarize the sequence of operations used to turn " "the source number into target number.",
    },
    {
        "recipient": code_writer_agent,
        "message": "Write a Python script to verify the arithmetic operations is correct.",
        "summary_method": "reflection_with_llm",
    },
    {
        "recipient": poetry_agent,
        "message": "Write a poem about it.",
        "max_turns": 1,
        "summary_method": "last_msg",
    },
]


arithmetic_agent.register_nested_chats(
    nested_chats,
    # The trigger function is used to determine if the agent should start the nested chat
    # given the sender agent.
    # In this case, the arithmetic agent will not start the nested chats if the sender is
    # from the nested chats' recipient to avoid recursive calls.
    trigger=lambda sender: sender not in [group_chat_manager_with_intros, code_writer_agent, poetry_agent],
)

# Instead of using `initiate_chat` method to start another conversation,
# we can use the `generate_reply` method to get single reply to a message directly.
reply = arithmetic_agent.generate_reply(
    messages=[{"role": "user", "content": "I have a number 3 and I want to turn it into 7."}]
)