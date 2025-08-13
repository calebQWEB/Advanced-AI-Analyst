import pandas as pd
import io
import aiohttp
from fastapi import HTTPException
from app.utils.logger import logger
from app.services.data_analysis_service import DataAnalysisService

class ParserService:
    def __init__(self):
        self.data_analysis_service = DataAnalysisService()

    async def parse_spreadsheet(self, file_url: str, file_type: str) -> tuple[str, str, dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        error_detail = await response.text()
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to download file: {response.reason} - {error_detail}"
                        )
                    file_content = await response.read()

            # Read file into pandas DataFrame
            if file_type == "csv":
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_type in ["xls", "xlsx"]:
                df = pd.read_excel(io.BytesIO(file_content), engine="openpyxl")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")

            # Generate raw text (markdown)
            raw_text = df.to_markdown(index=False)

            # Generate natural language description
            description = self._generate_description(df)
            
            # Compute actual business insights
            computed_insights = self.data_analysis_service.compute_business_insights(df)

            logger.info("Spreadsheet parsed successfully", file_url=file_url)
            return raw_text, description, computed_insights
        except Exception as e:
            logger.error("Failed to parse spreadsheet", error=str(e), file_url=file_url)
            raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

    def _generate_description(self, df: pd.DataFrame) -> str:
        try:
            columns = df.columns.tolist()
            dtypes = df.dtypes.to_dict()
            row_count = len(df)
            description = f"The spreadsheet contains {row_count} rows and {len(columns)} columns. "
            description += "Columns and their data types:\n"
            for col, dtype in dtypes.items():
                description += f"- {col}: {dtype}\n"
            
            # Basic summary for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if numeric_cols.any():
                description += "\nSummary of numeric columns:\n"
                for col in numeric_cols:
                    description += f"- {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}\n"
            
            return description
        except Exception as e:
            logger.error("Failed to generate description", error=str(e))
            return "Unable to generate description due to an error."