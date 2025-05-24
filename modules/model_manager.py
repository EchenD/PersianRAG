from llama_cpp import Llama
import gc

class ModelManager:
    def __init__(self):
        self.current_model = None
        self.current_model_key = None
        self.default_params = {
            "n_ctx": 4096,
            "n_threads": 6,
            "n_gpu_layers": 32,
            "offload_kqv": True,
            "flash_attn": True,
            "use_mmap": True,
            "keep_model_in_memory": True,
            "device_map": "auto",
            "verbose": True,
            "chat_format":"qwen"
        }

    def load_model(self, model_path, model_key, **kwargs):
        """Load a new model or skip if already loaded"""
        if self.current_model_key == model_key:
            print(f"Model {model_key} is already loaded.")
            return

        self.unload_model()

        print(f"Loading model {model_key} from {model_path}")
        # Combine default params with model-specific params
        model_params = {**self.default_params, **kwargs}
        self.current_model = Llama(model_path=model_path, **model_params)
        self.current_model_key = model_key

    def unload_model(self):
        """Unload the current model and free GPU resources."""
        if self.current_model:
            print(f"Unloading model {self.current_model_key}")
            del self.current_model
            del self.current_model_key
            gc.collect()
            self.current_model = None
            self.current_model_key = None

    def get_current_model(self):
        """Return the currently loaded model"""
        return self.current_model