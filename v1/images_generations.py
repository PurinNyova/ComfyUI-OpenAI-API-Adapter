# v1/images_generations.py
import base64
import time
import logging
import requests
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from config import COMFYUI_BASE_URL, SAVE_IMAGE_NODE_ID, APIKEY, config, supported_models, parse_size, load_workflow

logger = logging.getLogger(__name__)
router = APIRouter()

async def verify_api_key(authorization: Optional[str] = Header(None, alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    token = authorization.split(" ")[1].strip()
    if token != APIKEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return token

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = "hassaku-xl-illustrious-v22"  #default
    n: Optional[int] = 1
    size: Optional[str] = "1024x1024"
    quality: Optional[str] = "standard"  # Ignored because comfy don't use this
    response_format: Optional[str] = "url"

class ImageGenerationResponse(BaseModel):
    created: int
    data: List[Dict[str, Any]]

@router.post("/images/generations", response_model=ImageGenerationResponse)
async def generate_images(
    request: ImageGenerationRequest,
    api_key: str = Depends(verify_api_key)
):
    if request.model not in supported_models:
        raise HTTPException(status_code=400, detail=f"Only models {supported_models} are supported.")
    
    model_config = next(m for m in config["models"] if m["id"] == request.model)
    ckpt_name = model_config.get("ckpt_name")
    
    if request.n != 1:
        raise HTTPException(status_code=400, detail="Only n=1 is supported for simplicity.")
    
    width, height = parse_size(request.size)
    seed = time.time() #can replace with random if needed
    date_str = time.strftime("%Y-%m-%d")
    filename_prefix = f"{date_str}/ComfyUI"
    subfolder = date_str
    
    workflow = load_workflow(model_config)
    
    # hardcoded keys for now. a bit difficult to parse general workflows
    workflow["68"]["inputs"]["noise_seed"] = seed
    workflow["69"]["inputs"]["width"] = width
    workflow["69"]["inputs"]["height"] = height
    workflow["81"]["inputs"]["filename_prefix"] = filename_prefix
    workflow["96"]["inputs"]["text"] = request.prompt
    
    if ckpt_name:
        workflow["90"]["inputs"]["ckpt_name"] = ckpt_name
    
    data = {
        "prompt": workflow
    }
    
    # Log before queuing
    logger.info(f"Queuing image generation to ComfyUI: prompt='{request.prompt}', size={width}x{height}, seed={seed}, filename_prefix={filename_prefix}, model={request.model}")
    
    # Queue
    try:
        queue_response = requests.post(f"{COMFYUI_BASE_URL}/prompt", json=data)
        queue_response.raise_for_status()
        prompt_id = queue_response.json()["prompt_id"]
        logger.info(f"Prompt queued successfully in ComfyUI. Prompt ID: {prompt_id}")
    except requests.RequestException as e:
        logger.error(f"Failed to queue prompt in ComfyUI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue prompt in ComfyUI: {e}")
    
    # wait
    max_wait = 300 # 5mnt
    elapsed = 0
    logger.info(f"Starting polling for ComfyUI prompt completion: {prompt_id} (max wait: {max_wait}s)")
    
    while elapsed < max_wait:
        try:
            history_response = requests.get(f"{COMFYUI_BASE_URL}/history/{prompt_id}")
            history_response.raise_for_status()
            history = history_response.json()
            
            if prompt_id in history:
                outputs = history[prompt_id]["outputs"]
                if str(SAVE_IMAGE_NODE_ID) in outputs:  # SaveImage node
                    save_node = outputs[str(SAVE_IMAGE_NODE_ID)]
                    if "images" in save_node and save_node["images"]:
                        # get img
                        filename = save_node["images"][0]["filename"]
                        logger.info(f"Generation complete for ComfyUI prompt {prompt_id}. Fetching image: {filename}")
                        
                        img_response = requests.get(f"{COMFYUI_BASE_URL}/view?filename={filename}&subfolder={subfolder}&type=output")
                        img_response.raise_for_status()
                        
                        # b64
                        img = Image.open(BytesIO(img_response.content))
                        buffered = BytesIO()
                        img.save(buffered, format="PNG")
                        img_b64 = base64.b64encode(buffered.getvalue()).decode()
                        
                        logger.info(f"Image fetched, processed, and base64-encoded successfully for ComfyUI prompt {prompt_id}. Size: {img.size}")
                        
                        return ImageGenerationResponse(
                            created=int(time.time()),
                            data=[{
                                "url": f"data:image/png;base64,{img_b64}",
                                "b64_json": img_b64,
                                "revised_prompt": request.prompt 
                            }]
                        )
            else:
                logger.debug(f"ComfyUI history check for prompt {prompt_id}: No history yet (elapsed: {elapsed}s)")
        except requests.RequestException as e:
            logger.warning(f"Transient error during ComfyUI history fetch for prompt {prompt_id}: {e} (elapsed: {elapsed}s)")
        
        time.sleep(1)
        elapsed += 1
    
    logger.error(f"Image generation timed out for ComfyUI prompt {prompt_id} after {max_wait}s")
    raise HTTPException(status_code=500, detail="Generation timed out")