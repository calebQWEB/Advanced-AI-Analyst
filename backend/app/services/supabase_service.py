from supabase import create_client, Client
from app.config.settings import settings
from app.utils.logger import logger
from fastapi import HTTPException
import datetime
from datetime import timedelta

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)

    async def upload_file(self, file: bytes, file_name: str, user_id: str) -> str:
        try:
            bucket = "spreadsheets"
            file_path = f"{user_id}/{file_name}"
            
            # Proper MIME type detection
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = "application/octet-stream"
            
            response = self.client.storage.from_(bucket).upload(
                file_path,
                file,
                file_options={"content-type": content_type}
            )
            
            # Check upload success
            if hasattr(response, 'error') and response.error:
                raise HTTPException(status_code=400, detail=f"Upload failed: {response.error}")
            
            # Generate signed URL - check actual response structure
            signed_url_response = self.client.storage.from_(bucket).create_signed_url(file_path, expires_in=3600)
            
            # Handle different possible response structures
            if isinstance(signed_url_response, str):
                file_url = signed_url_response
            elif isinstance(signed_url_response, dict):
                file_url = signed_url_response.get('signedURL') or signed_url_response.get('signed_url')
                if not file_url:
                    raise HTTPException(status_code=500, detail="Failed to generate signed URL")
            else:
                raise HTTPException(status_code=500, detail="Unexpected signed URL response format")
            
            logger.info("File uploaded successfully", file_name=file_name, user_id=user_id, file_url=file_url)
            return file_url
            
        except Exception as e:
            logger.error("File upload failed", error=str(e), file_name=file_name, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

    async def save_file_metadata(self, file_name: str, file_url: str, user_id: str, file_size: int, file_type: str):
        try:
            data = {
                "filename": file_name,
                "file_path": file_url,
                "user_id": user_id,
                "file_size": file_size,
                "file_type": file_type,
                "status": "uploaded"
            }
            response = self.client.from_("uploaded_files").insert(data).execute()
            if response.data:
                logger.info("File metadata saved", file_name=file_name, user_id=user_id)
                return response.data
            else:
                raise Exception("Failed to save file metadata: No data returned")
        except Exception as e:
            logger.error("Failed to save file metadata", error=str(e), file_name=file_name, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to save file metadata: {str(e)}")

    async def list_user_files(self, user_id: str):
        try:
            response = self.client.from_("uploaded_files").select("*").eq("user_id", user_id).execute()
            if response.data is not None:
                logger.info("Retrieved user files", user_id=user_id, file_count=len(response.data))
                return response.data
            else:
                logger.info("No files found for user", user_id=user_id)
                return []
        except Exception as e:
            logger.error("Failed to list user files", error=str(e), user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

    async def get_file_by_id(self, file_id: str, user_id: str):
        try:
            response = self.client.from_("uploaded_files").select("*").eq("id", file_id).eq("user_id", user_id).single().execute()
            if response.data:
                logger.info("Retrieved file by ID", file_id=file_id, user_id=user_id)
                return response.data
            else:
                raise HTTPException(status_code=404, detail="File not found")
        except Exception as e:
            logger.error("Failed to retrieve file by ID", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")

    async def delete_file(self, file_id: str, user_id: str):
        try:
            # Get file metadata to obtain file_path
            file = await self.get_file_by_id(file_id, user_id)
            file_path = file["file_path"].split("?")[0].split("spreadsheets/")[1]  # Extract path from signed URL

            # Delete chat history
            self.client.from_("chat_history").delete().eq("file_id", file_id).eq("user_id", user_id).execute()
            logger.info("Chat history deleted", file_id=file_id, user_id=user_id)

            # Clear analysis_id in uploaded_files to avoid foreign key violation
            self.client.from_("uploaded_files").update({"analysis_id": None}).eq("id", file_id).eq("user_id", user_id).execute()
            logger.info("Cleared analysis_id in uploaded_files", file_id=file_id, user_id=user_id)

            # Delete analysis
            self.client.from_("file_analyses").delete().eq("file_id", file_id).eq("user_id", user_id).execute()
            logger.info("File analysis deleted", file_id=file_id, user_id=user_id)

            # Delete file metadata
            response = self.client.from_("uploaded_files").delete().eq("id", file_id).eq("user_id", user_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="File not found")
            logger.info("File metadata deleted", file_id=file_id, user_id=user_id)

            # Delete file from storage
            self.client.storage.from_("spreadsheets").remove([file_path])
            logger.info("File deleted from storage", file_id=file_id, user_id=user_id, file_path=file_path)

            return {"message": "File and associated data deleted successfully"}
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("Failed to delete file", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    async def update_file_status(self, file_id: str, user_id: str, status: str):
        try:
            response = self.client.from_("uploaded_files").update({"status": status}).eq("id", file_id).eq("user_id", user_id).execute()
            if response.data:
                logger.info("File status updated", file_id=file_id, user_id=user_id, status=status)
                return response.data
            else:
                raise HTTPException(status_code=404, detail="File not found")
        except Exception as e:
            logger.error("Failed to update file status", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to update file status: {str(e)}")

    async def save_analysis_result(self, file_id: str, user_id: str, raw_text: str, description: str, insights: dict):
        try:
            # Insert analysis result
            data = {
                "file_id": file_id,
                "user_id": user_id,
                "raw_text": raw_text,
                "description": description,
                "insights": insights,
                "status": "completed"
            }
            response = self.client.from_("file_analyses").insert(data).execute()
            if not response.data:
                raise Exception("Failed to save analysis result: No data returned")
            
            analysis_id = response.data[0]["id"]
            logger.info("Analysis result saved", file_id=file_id, user_id=user_id, analysis_id=analysis_id)

            # Update uploaded_files with analysis_id
            update_response = self.client.from_("uploaded_files").update({"analysis_id": analysis_id}).eq("id", file_id).eq("user_id", user_id).execute()
            if not update_response.data:
                raise Exception("Failed to update analysis_id in uploaded_files")

            logger.info("Updated analysis_id in uploaded_files", file_id=file_id, analysis_id=analysis_id)
            return response.data
        except Exception as e:
            logger.error("Failed to save analysis result", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to save analysis result: {str(e)}")

    async def get_analysis_by_file_id(self, file_id: str, user_id: str):
        try:
            response = self.client.from_("file_analyses").select("*").eq("file_id", file_id).eq("user_id", user_id).single().execute()
            if response.data:
                logger.info("Retrieved analysis by file ID", file_id=file_id, user_id=user_id)
                return response.data
            else:
                raise HTTPException(status_code=404, detail="Analysis not found")
        except Exception as e:
            logger.error("Failed to retrieve analysis", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")
        
    async def save_chat_history(self, file_id: str, analysis_id: str, user_id: str, question: str, answer: str):
        try:
            # Enforce message count limit (100 messages per file)
            count_response = self.client.from_("chat_history").select("id", count="exact").eq("file_id", file_id).eq("user_id", user_id).execute()
            message_count = count_response.count if count_response.count is not None else 0
            if message_count >= 100:
                # Delete oldest messages to keep under limit
                oldest_response = self.client.from_("chat_history").select("id").eq("file_id", file_id).eq("user_id", user_id).order("created_at").limit(message_count - 99).execute()
                if oldest_response.data:
                    oldest_ids = [record["id"] for record in oldest_response.data]
                    self.client.from_("chat_history").delete().in_("id", oldest_ids).execute()
                    logger.info("Deleted oldest chat messages to enforce limit", file_id=file_id, user_id=user_id, deleted_count=len(oldest_ids))

            # Enforce time-based limit (30 days)
            # 🐛 FIX: Calculate the date 30 days ago in Python instead of passing a raw SQL string.
            thirty_days_ago = datetime.datetime.now() - timedelta(days=30)
            self.client.from_("chat_history").delete().eq("file_id", file_id).eq("user_id", user_id).lt("created_at", thirty_days_ago).execute()

            # Insert new chat history
            data = {
                "file_id": file_id,
                "analysis_id": analysis_id,
                "user_id": user_id,
                "question": question,
                "answer": answer
            }
            response = self.client.from_("chat_history").insert(data).execute()
            if response.data:
                logger.info("Chat history saved", file_id=file_id, user_id=user_id)
                return response.data
            else:
                raise Exception("Failed to save chat history: No data returned")
        except Exception as e:
            logger.error("Failed to save chat history", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to save chat history: {str(e)}")


    async def get_chat_history(self, file_id: str, user_id: str):
        try:
            response = self.client.from_("chat_history").select("question, answer, created_at").eq("file_id", file_id).eq("user_id", user_id).order("created_at").execute()
            if response.data is not None:
                logger.info("Retrieved chat history", file_id=file_id, user_id=user_id, message_count=len(response.data))
                return response.data
            else:
                logger.info("No chat history found", file_id=file_id, user_id=user_id)
                return []
        except Exception as e:
            logger.error("Failed to retrieve chat history", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")