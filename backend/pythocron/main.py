from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from crontab import CronTab
import pathlib
from pythocron import config, schemas, utils
from functools import lru_cache


@lru_cache()
def get_settings():
    return config.Settings()


app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    pathlib.Path(get_settings().logs_dir_path).mkdir(parents=True, exist_ok=True)


@app.get("/")
def root(settings: config.Settings = Depends(get_settings)):
    return {"message": "Hello pythocron"}


@app.post("/backend/pythocron")
def create_pythocron(
    pythocron: schemas.PythocronCreate,
    settings: config.Settings = Depends(get_settings),
):
    pythocron_id = utils.generate_id()
    pythocron_logfile_path = f"{settings.logs_dir_path}/{pythocron_id}.log"

    cron = CronTab(user="root")
    job = cron.new(command=f"echo hello_world >> {pythocron_logfile_path}")
    job.minute.every(1)
    cron.write()
    return {"pythocron_id": pythocron_id}


@app.get("/backend/pythocron/{pythocron_id}/logs")
def read_pythocron_logs(pythocron_id):
    logs_dir_path = "/app/data/logs"
    pythocron_logfile_path = f"{logs_dir_path}/{pythocron_id}.log"
    try:
        return open(pythocron_logfile_path).readlines()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Pythocron logs not found")
