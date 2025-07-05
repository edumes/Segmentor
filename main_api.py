from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import subprocess
import uuid
import zipfile
from typing import Dict, List, Optional, Set
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio

app = FastAPI(title="Video Segmenter API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
UPLOAD_DIR = "uploads"
QUEUE_FILE = "queue.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Modelos
class QueueItem(BaseModel):
    id: str
    fileName: str
    status: str
    progress: float
    selectedMinutes: Dict[str, List[int]]
    error: Optional[str] = None
    result: Optional[Dict[str, str]] = None
    createdAt: str
    updatedAt: str

    def dict(self, *args, **kwargs):
        return {
            "id": self.id,
            "fileName": self.fileName,
            "status": self.status,
            "progress": self.progress,
            "selectedMinutes": self.selectedMinutes,
            "error": self.error,
            "result": self.result,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }

# Gerenciamento da Fila
def load_queue() -> Dict[str, QueueItem]:
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            data = json.load(f)
            return {k: QueueItem(**v) for k, v in data.items()}
    return {}

def save_queue(queue: Dict[str, QueueItem]):
    with open(QUEUE_FILE, 'w') as f:
        json.dump({k: v.dict() for k, v in queue.items()}, f, indent=2)

async def broadcast_queue_update(queue: Dict[str, QueueItem]):
    await manager.broadcast({
        "type": "queue_update",
        "items": [item.dict() for item in queue.values()]
    })

# Função refatorada de segmentação (sem GUI)
def extract_segment(input_video: str, output_path: str, start_time: float, duration: float, vertical: bool = False) -> None:
    ffmpeg_cmd = [
        'ffmpeg',
        '-ss', str(start_time),
        '-i', input_video,
        '-t', str(duration),
        '-c:v', 'h264_nvenc',
        '-preset', 'p7',
        '-cq', '20',
        '-profile:v', 'high',
        '-rc', 'vbr_hq',
        '-bf', '4',
    ]
    if vertical:
        ffmpeg_cmd += [
            '-vf', "crop=ih*(9/16):ih:(iw-ih*(9/16))/2:0,scale=1080:1920"
        ]
    ffmpeg_cmd += [
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-y',
        output_path
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg falhou: {result.stderr.decode()}")

async def process_video(item_id: str, background_tasks: BackgroundTasks):
    queue = load_queue()
    if item_id not in queue:
        return

    item = queue[item_id]
    item.status = "processing"
    item.updatedAt = datetime.now().isoformat()
    save_queue(queue)
    
    # Broadcast queue update
    await broadcast_queue_update(queue)

    try:
        # Parse dos índices
        default_idxs = item.selectedMinutes.get("default", [])
        vertical_idxs = item.selectedMinutes.get("vertical", [])

        # Pasta temporária para processamento
        work_dir = os.path.join(UPLOAD_DIR, item_id)
        os.makedirs(work_dir, exist_ok=True)

        video_path = os.path.join(work_dir, item.fileName)
        output_folder = os.path.join(work_dir, "output")
        os.makedirs(output_folder, exist_ok=True)

        all_idxs = set(default_idxs + vertical_idxs)
        base = os.path.splitext(item.fileName)[0]
        total_segments = len(all_idxs)
        processed_segments = 0

        for minute in all_idxs:
            start = minute * 60
            duration = 60
            if minute in default_idxs:
                out_def = os.path.join(output_folder, f"{base}_seg_{minute+1}_default.mp4")
                extract_segment(video_path, out_def, start, duration, vertical=False)
            if minute in vertical_idxs:
                out_vert = os.path.join(output_folder, f"{base}_seg_{minute+1}_vertical.mp4")
                extract_segment(video_path, out_vert, start, duration, vertical=True)
            
            processed_segments += 1
            item.progress = (processed_segments / total_segments) * 100
            item.updatedAt = datetime.now().isoformat()
            save_queue(queue)
            await broadcast_queue_update(queue)

        # Empacota tudo em um ZIP para download
        zip_path = os.path.join(work_dir, f"{base}_segments.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for fname in os.listdir(output_folder):
                zipf.write(os.path.join(output_folder, fname), arcname=fname)

        item.status = "completed"
        item.result = {
            "downloadUrl": f"/download/{item_id}",
            "fileName": f"{base}_segments.zip"
        }
    except Exception as e:
        item.status = "failed"
        item.error = str(e)
    finally:
        item.updatedAt = datetime.now().isoformat()
        save_queue(queue)
        await broadcast_queue_update(queue)

@app.post("/upload/")
async def upload_video(
    file: UploadFile = File(...),
    defaults: str = Form(""),   # índices de minutos separados por vírgula
    verticals: str = Form("")   # índices de minutos separados por vírgula
):
    try:
        # Parse dos índices
        default_idxs = [int(x) for x in defaults.split(',') if x.strip()] if defaults else []
        vertical_idxs = [int(x) for x in verticals.split(',') if x.strip()] if verticals else []

        # Criar ID único para o item
        item_id = str(uuid.uuid4())
        
        # Salvar arquivo
        file_path = os.path.join(UPLOAD_DIR, item_id, file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Criar item na fila
        now = datetime.now().isoformat()
        item = QueueItem(
            id=item_id,
            fileName=file.filename,
            status="pending",
            progress=0,
            selectedMinutes={
                "default": default_idxs,
                "vertical": vertical_idxs
            },
            createdAt=now,
            updatedAt=now
        )

        queue = load_queue()
        queue[item_id] = item
        save_queue(queue)
        
        # Broadcast queue update
        await broadcast_queue_update(queue)

        return {"id": item_id, "status": "pending"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queue/")
async def get_queue():
    queue = load_queue()
    return list(queue.values())

@app.get("/queue/{item_id}")
async def get_queue_item(item_id: str):
    queue = load_queue()
    if item_id not in queue:
        raise HTTPException(status_code=404, detail="Item not found")
    return queue[item_id]

@app.post("/queue/{item_id}/process")
async def process_queue_item(item_id: str, background_tasks: BackgroundTasks):
    queue = load_queue()
    if item_id not in queue:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = queue[item_id]
    if item.status != "pending":
        raise HTTPException(status_code=400, detail="Item is not pending")
    
    background_tasks.add_task(process_video, item_id, background_tasks)
    return {"status": "processing"}

@app.delete("/queue/{item_id}")
async def delete_queue_item(item_id: str):
    queue = load_queue()
    if item_id not in queue:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Remover arquivos
    work_dir = os.path.join(UPLOAD_DIR, item_id)
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    
    # Remover da fila
    del queue[item_id]
    save_queue(queue)
    
    # Broadcast queue update
    await broadcast_queue_update(queue)
    
    return {"status": "deleted"}

@app.get("/download/{item_id}")
async def download_result(item_id: str):
    queue = load_queue()
    if item_id not in queue:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = queue[item_id]
    if item.status != "completed" or not item.result:
        raise HTTPException(status_code=400, detail="Item is not completed")
    
    work_dir = os.path.join(UPLOAD_DIR, item_id)
    zip_path = os.path.join(work_dir, item.result["fileName"])
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(zip_path, filename=item.result["fileName"])

@app.websocket("/ws/queue")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial queue state
        queue = load_queue()
        await websocket.send_json({
            "type": "queue_update",
            "items": [item.dict() for item in queue.values()]
        })
        
        # Keep connection alive and handle disconnection
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)