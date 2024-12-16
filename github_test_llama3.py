
# import autogen
# from autogen import UserProxyAgent, AssistantAgent, config_list_from_json, GroupChat, GroupChatManager
# from typing import Annotated
# import os
# import requests
# import re
# import json


# # config_list = autogen.config_list_from_json(
# #     env_or_file = "OAI_CONFIG_LIST.json",
# #     filter_dict = {"model":"gpt-4o"},
# # )
# # llm_config = {"config_list": config_list}





# #configuration with llama3 with ollama
# config_list = [
#     {
#         "model": "llama3",
#         "base_url": "http://localhost:11434/v1",
#         'api_key': 'ollama',
#     },
# ]
# llm_config = {"config_list": config_list}



# file_listing_agent = AssistantAgent(
    
#     name="file_listing_agent",
    
#     system_message="""
#     you can list all files in a github repository using the function list_files,
#     To call this function, respond using the exact format:
#     <function=list_files>{"repo_url": "<repo_url>"}</function>
#     do not add any extra text.just out this format strictly
#     """,
    
#     llm_config=llm_config,
# )

# content_fetcher_agent = AssistantAgent(
#     name="content_fetcher_agent",
#     system_message="you execute the fetch_file_content function and return the content of each file from list_files function.",
#     llm_config=llm_config,
# )

# UserProxy = UserProxyAgent(
#     name="UserProxy",
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=2,
#     code_execution_config=False,
# )  
    



# #define a function to list files in repository
# #
# # Skill: List Repository Files
# def list_files(repo_url:Annotated[str, "The URL of the GitHub repository"]) -> list:
#     """
#     List files in a given GitHub repository.

#     Args:
#     repo_url (str): The URL of the repository to list files from, e.g. "https://github.com/owner/repo".

#     Returns:
#     list: List of file names in the repository, including files in subdirectories.
#     dict: A dictionary containing an error message if the API request fails, e.g. {"error": "Failed to list files: 404"}.

#     Raises:
#     Exception: If the API request fails with a status code other than 200.
#     """
#     owner, repo_name = repo_url.split("/")[-2:]
#     api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
#     # Global Headers for Authentication
#     headers = {
#         "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"  # Use your GitHub token
#     }
#     response = requests.get(api_url, headers=headers)
#     if response.status_code == 200:
#         files = []
#         for item in response.json():
#             if item["type"] == "file":
#                 files.append(item["path"])
#             elif item["type"] == "dir":
#                 # Recursive call for directories
#                 nested_files = list_files(f"{repo_url}/{item['path']}")
#                 if isinstance(nested_files, list):
#                     files.extend(nested_files)
#         return files
#     else:
#         return {"error": f"Failed to list files: {response.status_code}"}  



# # Parse Function Call from Llama3 Response
# def parse_function_call(response_content):
#     """
#     Extract function call and arguments from Llama3's response using regex.
#     """
#     function_pattern = r"<function=(\w+)>(.*?)</function>"
#     match = re.search(function_pattern, response_content)
#     if match:
#         function_name = match.group(1)
#         arguments = json.loads(match.group(2))
#         return function_name, arguments
#     return None, None




# def main():
#     # UserProxy asks the file_listing_agent to list files
#     user_message = "Please list all files in the repository: https://github.com/Zohreh6384NKH/AutoGen_tutorial"

#     # Step 1: Send the message to the agent
#     response = file_listing_agent.generate_reply(messages=[{"role": "user", "content": user_message}])

#     # Step 2: Parse the response for a function call
#     response_content = response.get("content", "")
#     function_name, arguments = parse_function_call(response_content)

#     if function_name == "list_files":
#         # Execute the function manually
#         repo_url = arguments.get("repo_url")
#         files = list_files(repo_url)
#         print("Function Output: List of Files:", files)
#     else:
#         print("Llama's Response:", response_content)

# # Run the Script
# if __name__ == "__main__":
#     main()
import autogen
from autogen import AssistantAgent
from typing import Annotated
import os
import requests
import re
import json

# Configuration with Llama3 using Ollama
config_list = [
    {
        "model": "llama3",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    },
]
llm_config = {"config_list": config_list}

# Define the file listing agent
file_listing_agent = AssistantAgent(
    name="file_listing_agent",
    system_message="""
    You can list all files in a GitHub repository using the function list_files.
    To call this function, respond using the exact format:
    <function=list_files>{"repo_url": "<repo_url>"}</function>
    Do not add any extra text, just output this format strictly.
    """,
    llm_config=llm_config,
)

# Function to list files in a GitHub repository
def list_files(repo_url: Annotated[str, "The URL of the GitHub repository"]) -> list:
    """
    List all files in a GitHub repository.
    """
    owner, repo_name = repo_url.split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
    headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        files = []
        for item in response.json():
            if item["type"] == "file":
                files.append(item["path"])
            elif item["type"] == "dir":
                # Recursive call for directories
                nested_files = list_files(f"{repo_url}/{item['path']}")
                if isinstance(nested_files, list):
                    files.extend(nested_files)
        return files
    else:
        return {"error": f"Failed to list files: {response.status_code}"}

# Function to parse the function call response
def parse_function_call(response_content):
    """
    Extract function call and arguments from Llama3's response using regex.
    """
    function_pattern = r"<function=(\w+)>(.*?)</function>"
    match = re.search(function_pattern, response_content)
    if match:
        function_name = match.group(1)
        arguments = json.loads(match.group(2))
        return function_name, arguments
    return None, None

# Main workflow
def main():
    # UserProxy sends the message to list files
    user_message = "Please list all files in the repository: https://github.com/Zohreh6384NKH/AutoGen_tutorial"

    print("User Message:", user_message)

    # Generate response from the agent
    response = file_listing_agent.generate_reply(messages=[{"role": "user", "content": user_message}])

    # Attempt to parse the response as JSON
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        print("Failed to parse response as JSON. Treating as plain text.")
        response = {"content": response}  # Wrap response as a dictionary

    # Ensure response is treated as a string
    response_content = response.get("content", "")

    print("Llama3 Response:", response_content)

    # Parse function call from the response
    function_name, arguments = parse_function_call(response_content)

    if function_name == "list_files":
        # Execute the function manually
        repo_url = arguments.get("repo_url")
        print("Function Detected:", function_name)
        print("Repository URL:", repo_url)

        files = list_files(repo_url)
        print("\nFunction Output: List of Files:")
        print(files)
    else:
        print("\nLlama's Response (No Function Call Detected):")
        print(response_content)

# Run the script
if __name__ == "__main__":
    main()