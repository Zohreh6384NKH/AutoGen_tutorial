import autogen 
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json



# Load configuration for the AssistantAgent
config_list = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST.json",
    filter_dict={"model": "gpt-4o"},
)
llm_config = {"config_list": config_list}

#create an assistant agent named asssitant
assistant = AssistantAgent(
    name="assistant",
    llm_config={"config_list":config_list,
    "seed":0,
    "temperature": 0}
)
#create a user proxy agent named user_proxy
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir":"coding",
        "use_docker":True,
    },
)

# Start the chat
user_proxy.initiate_chat(
    assistant,
    message="""What date is today? Compare the year-to-date gain for META and TESLA.""",
)