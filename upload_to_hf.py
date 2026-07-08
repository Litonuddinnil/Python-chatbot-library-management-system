from huggingface_hub import HfApi

# Hugging Face API  
api = HfApi()

#  fine tunnnin hugging face upload 
api.upload_folder(
    folder_path="./my-library-llm",          #  local mode folder
    repo_id="your-username/my-library-llm",   #  hf usernamae and new repository
    repo_type="model"
)

print("successfully Hugging Face uploaded")