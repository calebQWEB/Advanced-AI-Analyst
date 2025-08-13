from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from app.utils.logger import logger
from fastapi import HTTPException
from together import AsyncTogether
from app.config.settings import settings
import json

class GraphState(TypedDict):
    raw_text: str
    description: str
    insights: Dict[str, Any]

class LangGraphService:
    def __init__(self):
        self.client = AsyncTogether(api_key=settings.together_api_key)

    def _truncate_text(self, text: str, max_chars: int = 2000) -> str:
        """Truncate text to avoid token limits"""
        if len(text) <= max_chars:
            return text
        
        # Try to truncate at a reasonable breakpoint
        truncated = text[:max_chars]
        
        # Find the last complete line
        last_newline = truncated.rfind('\n')
        if last_newline > max_chars * 0.8:  # If we can keep 80% of content
            truncated = truncated[:last_newline]
        
        return truncated + "\n... (truncated for analysis)"

    async def generate_insights(self, raw_text: str, description: str) -> Dict[str, Any]:
        try:
            # Truncate raw_text to prevent token limit issues
            truncated_text = self._truncate_text(raw_text, 1500)
            truncated_description = self._truncate_text(description, 500)
            
            logger.info("Starting insight generation", 
                       raw_text_length=len(raw_text), 
                       truncated_length=len(truncated_text))

            # Define the LangGraph workflow
            workflow = StateGraph(GraphState)

            # Nodes with better error handling
            async def analyze_trends(state: GraphState) -> GraphState:
                try:
                    prompt = f"""
                    Analyze the following spreadsheet data to identify 2-3 key business trends.
                    
                    Data Sample:
                    {state['raw_text'][:800]}
                    
                    Description:
                    {state['description']}
                    
                    Return a JSON object with a 'trends' key containing a list of trend descriptions.
                    Example: {{"trends": ["Sales increased by 15% month-over-month", "Technology products show highest growth"]}}
                    """
                    
                    response = await self.client.chat.completions.create(
                        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        max_tokens=300,
                        temperature=0.3
                    )
                    
                    content = response.choices[0].message.content.strip()
                    logger.info("Raw trends response", content=content[:200])
                    
                    try:
                        trends_data = json.loads(content)
                        trends = trends_data.get("trends", ["Unable to identify specific trends"])
                    except json.JSONDecodeError as e:
                        logger.warning("Failed to parse trends JSON", error=str(e), content=content[:100])
                        trends = ["Error parsing trends analysis"]
                    
                    state["insights"]["trends"] = trends
                    logger.info("Generated trends", trends_count=len(trends))
                    return state
                    
                except Exception as e:
                    logger.error("Error in analyze_trends", error=str(e), error_type=type(e).__name__)
                    state["insights"]["trends"] = ["Error analyzing trends"]
                    return state

            async def analyze_anomalies(state: GraphState) -> GraphState:
                try:
                    prompt = f"""
                    Analyze the following data to identify 1-2 anomalies or unusual patterns.
                    
                    Data Sample:
                    {state['raw_text'][:800]}
                    
                    Description:
                    {state['description']}
                    
                    Return a JSON object with an 'anomalies' key containing a list of anomaly descriptions.
                    Example: {{"anomalies": ["Unusually high returns in March", "Spike in weekend sales"]}}
                    """
                    
                    response = await self.client.chat.completions.create(
                        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        max_tokens=300,
                        temperature=0.3
                    )
                    
                    content = response.choices[0].message.content.strip()
                    logger.info("Raw anomalies response", content=content[:200])
                    
                    try:
                        anomalies_data = json.loads(content)
                        anomalies = anomalies_data.get("anomalies", ["No significant anomalies detected"])
                    except json.JSONDecodeError as e:
                        logger.warning("Failed to parse anomalies JSON", error=str(e), content=content[:100])
                        anomalies = ["Error parsing anomalies analysis"]
                    
                    state["insights"]["anomalies"] = anomalies
                    logger.info("Generated anomalies", anomalies_count=len(anomalies))
                    return state
                    
                except Exception as e:
                    logger.error("Error in analyze_anomalies", error=str(e), error_type=type(e).__name__)
                    state["insights"]["anomalies"] = ["Error analyzing anomalies"]
                    return state

            async def generate_predictions(state: GraphState) -> GraphState:
                try:
                    prompt = f"""
                    Based on the following data, generate 1-2 business predictions or recommendations.
                    
                    Data Sample:
                    {state['raw_text'][:800]}
                    
                    Description:
                    {state['description']}
                    
                    Return a JSON object with a 'predictions' key containing a list of predictions.
                    Example: {{"predictions": ["Expect 10% growth next quarter", "Consider expanding top-performing regions"]}}
                    """
                    
                    response = await self.client.chat.completions.create(
                        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        max_tokens=300,
                        temperature=0.3
                    )
                    
                    content = response.choices[0].message.content.strip()
                    logger.info("Raw predictions response", content=content[:200])
                    
                    try:
                        predictions_data = json.loads(content)
                        predictions = predictions_data.get("predictions", ["Unable to generate specific predictions"])
                    except json.JSONDecodeError as e:
                        logger.warning("Failed to parse predictions JSON", error=str(e), content=content[:100])
                        predictions = ["Error parsing predictions analysis"]
                    
                    state["insights"]["predictions"] = predictions
                    logger.info("Generated predictions", predictions_count=len(predictions))
                    return state
                    
                except Exception as e:
                    logger.error("Error in generate_predictions", error=str(e), error_type=type(e).__name__)
                    state["insights"]["predictions"] = ["Error generating predictions"]
                    return state

            # Add nodes
            workflow.add_node("analyze_trends", analyze_trends)
            workflow.add_node("analyze_anomalies", analyze_anomalies)  
            workflow.add_node("generate_predictions", generate_predictions)

            # Define edges
            workflow.set_entry_point("analyze_trends")
            workflow.add_edge("analyze_trends", "analyze_anomalies")
            workflow.add_edge("analyze_anomalies", "generate_predictions")
            workflow.add_edge("generate_predictions", END)

            # Compile and run
            graph = workflow.compile()
            initial_state = GraphState(
                raw_text=truncated_text, 
                description=truncated_description, 
                insights={}
            )
            result = await graph.ainvoke(initial_state)

            logger.info("AI insights generated successfully")
            return result["insights"]
            
        except Exception as e:
            logger.error("Failed to generate insights", 
                        error=str(e), 
                        error_type=type(e).__name__)
            
            # Return fallback insights instead of raising exception
            return {
                "trends": ["Unable to analyze trends due to technical error"],
                "anomalies": ["Unable to analyze anomalies due to technical error"], 
                "predictions": ["Unable to generate predictions due to technical error"]
            }