from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from app.config.settings import settings
from app.utils.logger import logger
from app.services.supabase_service import SupabaseService
from app.utils.auth import get_current_user
from app.services.parser_service import ParserService
from app.services.langgraph_service import LangGraphService
from app.services.chat_service import ChatService
from app.services.pdf_export_service import PDFExportService 
import io

app = FastAPI(title="AI Analyst Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DETETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

supabase_service = SupabaseService()
parser_service = ParserService()
langgraph_service = LangGraphService()
chat_service = ChatService()
pdf_export_service = PDFExportService()

class ChatRequest(BaseModel):
    file_id: str
    question: str

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    try:
        # Validate file type
        file_ext = file.filename.split(".")[-1].lower()
        allowed_types = settings.allowed_file_types.split(",")
        if file_ext not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_types}")

        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(status_code=400, detail="File size exceeds limit")

        # Upload to Supabase
        file_url = await supabase_service.upload_file(file_content, file.filename, user_id)

        # Save metadata
        result = await supabase_service.save_file_metadata(
            file_name=file.filename,
            file_url=file_url,
            user_id=user_id,
            file_size=len(file_content),
            file_type=file_ext
        )
        
        logger.info("File processed successfully", file_name=file.filename, user_id=user_id)
        return {"file_url": file_url, "file_id": result[0]["id"]}
    except Exception as e:
        logger.error("Error processing file", error=str(e), file_name=file.filename)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files(user_id: str = Depends(get_current_user)):
    try:
        files = await supabase_service.list_user_files(user_id)
        return {"files": files}
    except Exception as e:
        logger.error("Error listing files", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_id}")
async def get_file(file_id: str, user_id: str = Depends(get_current_user)):
    try:
        file = await supabase_service.get_file_by_id(file_id, user_id)
        return file
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error retrieving file", error=str(e), file_id=file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/{file_id}")
async def analyze_file(file_id: str, user_id: str = Depends(get_current_user)):
    try:
        # Get file metadata
        file = await supabase_service.get_file_by_id(file_id, user_id)
        if file["status"] in ["processing", "analyzed"]:
            raise HTTPException(status_code=400, detail=f"File is already {file['status']}")

        # Update status to processing
        await supabase_service.update_file_status(file_id, user_id, "processing")

        try:
            # Parse spreadsheet (now returns computed insights too)
            raw_text, description, computed_insights = await parser_service.parse_spreadsheet(
                file["file_path"], file["file_type"]
            )

            # Generate AI insights using LangGraph (trends, anomalies, predictions)
            ai_insights = await langgraph_service.generate_insights(raw_text, description)
            
            # Combine computed insights with AI insights
            all_insights = {
                **computed_insights,  # Actual calculated data
                **ai_insights         # AI-generated trends/predictions
            }

            # Save analysis results
            analysis_result = await supabase_service.save_analysis_result(
                file_id, user_id, raw_text, description, all_insights
            )

            # Update file status to analyzed
            await supabase_service.update_file_status(file_id, user_id, "analyzed")

            logger.info("File analyzed successfully", file_id=file_id, user_id=user_id)
            return {
                "file_id": file_id,
                "analysis_id": analysis_result[0]["id"],
                "status": "analyzed"
            }
        except Exception as e:
            # Update status to error on failure
            await supabase_service.update_file_status(file_id, user_id, "error")
            raise
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error analyzing file", error=str(e), file_id=file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/analyses/{file_id}")
async def get_analysis(file_id: str, user_id: str = Depends(get_current_user)):
    try:
        analysis = await supabase_service.get_analysis_by_file_id(file_id, user_id)
        return analysis
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error retrieving analysis", error=str(e), file_id=file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat")
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    try:
        # Get analysis data
        analysis = await supabase_service.get_analysis_by_file_id(request.file_id, user_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found for this file")

        # Get chat history
        chat_history = await supabase_service.get_chat_history(request.file_id, user_id)

        # Generate answer
        answer = await chat_service.process_chat(
            file_id=request.file_id,
            user_id=user_id,
            question=request.question,
            analysis_data=analysis,
            chat_history=chat_history
        )

        # Save chat history
        await supabase_service.save_chat_history(
            file_id=request.file_id,
            analysis_id=analysis["id"],
            user_id=user_id,
            question=request.question,
            answer=answer
        )

        logger.info("Chat response generated", file_id=request.file_id, user_id=user_id)
        return {"file_id": request.file_id, "question": request.question, "answer": answer}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error processing chat", error=str(e), file_id=request.file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{file_id}")
async def get_chat_history(file_id: str, user_id: str = Depends(get_current_user)):
    try:
        chat_history = await supabase_service.get_chat_history(file_id, user_id)
        logger.info("Chat history retrieved", file_id=file_id, user_id=user_id, message_count=len(chat_history))
        return {"history": chat_history}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error retrieving chat history", error=str(e), file_id=file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/pdf/{file_id}")
async def export_pdf_report(
    file_id: str, 
    user_id: str = Depends(get_current_user)
):
    """Export analysis insights as a beautifully formatted PDF report"""
    try:
        # Get file metadata
        file = await supabase_service.get_file_by_id(file_id, user_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Debug logging
        logger.info("File data retrieved", file_data=file, file_id=file_id, user_id=user_id)
        
        if file["status"] != "analyzed":
            raise HTTPException(status_code=400, detail="File must be analyzed before exporting to PDF")

        # Get analysis data
        analysis = await supabase_service.get_analysis_by_file_id(file_id, user_id)
        if not analysis or not analysis.get("insights"):
            raise HTTPException(status_code=404, detail="No analysis insights found for this file")
        
        # Debug logging for analysis
        logger.info("Analysis data retrieved", analysis_keys=list(analysis.keys()) if analysis else [], file_id=file_id)

        # Extract the file name safely with multiple fallbacks
        file_name = (
            file.get("filename") or      # ✅ This is the correct field based on your debug
            file.get("file_name") or 
            file.get("name") or 
            file.get("original_name") or 
            f"File_{file_id[:8]}"
        )
        
        # Ensure it's a string and not empty
        if not isinstance(file_name, str) or not file_name.strip():
            file_name = f"Analysis_{file_id[:8]}"
            
        logger.info("Final file name determined", file_name=file_name, file_id=file_id)

        # Generate PDF
        pdf_content = await pdf_export_service.generate_insights_pdf(
            insights=analysis["insights"],
            file_name=file_name,
            user_id=user_id
        )

        # Create filename for download
        safe_filename = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_filename:  # Fallback if filename cleaning results in empty string
            safe_filename = f"Analysis_{file_id[:8]}"
        pdf_filename = f"{safe_filename}_Analysis_Report.pdf"
        
        logger.info("PDF filename created", pdf_filename=pdf_filename, file_id=file_id)

        logger.info("PDF report generated successfully", 
                   file_id=file_id, user_id=user_id, pdf_size=len(pdf_content))

        # Return PDF as downloadable response using StreamingResponse
        pdf_stream = io.BytesIO(pdf_content)
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={pdf_filename}",
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error generating PDF report", 
                    error=str(e), file_id=file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
    
@app.delete("/files/{file_id}")
async def delete_file(file_id: str, user_id: str = Depends(get_current_user)):
    try:
        await supabase_service.delete_file(file_id, user_id)
        logger.info("File deleted successfully", file_id=file_id, user_id=user_id)
        return {"message": "File and associated data deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error deleting file", error=str(e), file_id=file_id, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))