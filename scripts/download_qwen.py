import os
import json
from huggingface_hub import snapshot_download

def download_qwen_model(model_name="unsloth/Qwen3-14B-GGUF", output_dir="../models"):
    """
    Download Qwen model from Hugging Face and return the local path.
    """
    print(f"Downloading {model_name} to {output_dir}...")
    model_path = snapshot_download(
        repo_id=model_name,
        local_dir=os.path.abspath(output_dir),
        local_dir_use_symlinks=False,
        cache_dir=output_dir
    )
    print(f"Model downloaded to {model_path}")
    return model_path

def update_models_json(model_key, model_path, template_key="qwen3_nonthinking.jinja", models_file="../data/models.json"):
    """
    Update models.json with the new model path.
    """
    models = {}
    if os.path.exists(models_file):
        with open(models_file, "r", encoding="utf-8") as f:
            models = json.load(f)

    models[model_key] = {
        "path": model_path,
        "prompt_template_key": template_key,
        "params": {
            "n_ctx": 4096,
            "n_gpu_layers": 32
        }
    }

    with open(models_file, "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=4)
    print(f"Updated {models_file} with {model_key}")

if __name__ == "__main__":
    # Download Qwen2-7B-Instruct
    model_path = download_qwen_model()
    # Update models.json
    update_models_json("Qwen2-7B-Instruct", model_path)