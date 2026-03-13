
from fastapi import APIRouter, UploadFile, File
import pandas as pd
from ingestion.file_loader import FileLoader
from ingestion.schema_mapper import SchemaMapper
from processing.data_normalizer import DataNormalizer
from orchestrator.agent_orchestrator import AgentOrchestrator

router = APIRouter()

@router.post("/")
async def upload(files: list[UploadFile] = File(...)):

    loader = FileLoader()
    mapper = SchemaMapper()
    normalizer = DataNormalizer()
    orchestrator = AgentOrchestrator()

    dataframes = []

    for file in files:
        df = loader.load_excel(file.file)
        df = mapper.map_schema(df)
        df = normalizer.normalize(df)
        dataframes.append(df)

    df = pd.concat(dataframes)

    findings = orchestrator.run(df)

    return {"rows_processed": len(df), "findings": findings}
