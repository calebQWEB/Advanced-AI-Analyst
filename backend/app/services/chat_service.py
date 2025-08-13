from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from app.utils.logger import logger
from fastapi import HTTPException
from together import AsyncTogether
from app.config.settings import settings
import json

class ChatState(TypedDict):
    file_id: str
    user_id: str
    question: str
    analysis_data: Dict
    chat_history: List[Dict[str, str]]
    answer: str

class ChatService:
    def __init__(self):
        self.client = AsyncTogether(api_key=settings.together_api_key)

    async def process_chat(self, file_id: str, user_id: str, question: str, analysis_data: Dict, chat_history: List[Dict[str, str]]) -> str:
        try:
            # Define the LangGraph workflow
            workflow = StateGraph(ChatState)

            # Node to generate answer
            async def generate_answer(state: ChatState) -> ChatState:
                # Extract computed insights for direct answers
                insights = state['analysis_data'].get('insights', {})
                
                # Build context with computed data
                context_parts = [
                    f"Spreadsheet Description: {state['analysis_data']['description']}",
                    f"Previous Conversation: {self._format_chat_history(state['chat_history'])}"
                ]
                
                # Add specific computed insights
                if 'top_sales_reps' in insights:
                    best_rep = insights['top_sales_reps']['best_performer']
                    context_parts.append(f"Best Sales Rep: {best_rep['name']} with ${best_rep['total_sales']:,.2f} in total sales ({best_rep['transactions']} transactions)")
                    
                    all_reps = insights['top_sales_reps']['all_reps']
                    reps_summary = ", ".join([f"{rep['name']}: ${rep['total_sales']:,.2f}" for rep in all_reps[:5]])
                    context_parts.append(f"All Sales Reps Performance: {reps_summary}")

                if 'top_products' in insights:
                    top_products = insights['top_products'][:5]
                    products_summary = ", ".join([f"{prod['name']}: ${prod['total_revenue']:,.2f}" for prod in top_products])
                    context_parts.append(f"Top Products: {products_summary}")

                if 'top_customers' in insights:
                    top_customers = insights['top_customers'][:5]
                    customers_summary = ", ".join([f"{cust['name']}: ${cust['total_spent']:,.2f}" for cust in top_customers])
                    context_parts.append(f"Top Customers: {customers_summary}")

                if 'revenue_by_category' in insights:
                    categories = insights['revenue_by_category'][:5]
                    categories_summary = ", ".join([f"{cat['category']}: ${cat['revenue']:,.2f}" for cat in categories])
                    context_parts.append(f"Revenue by Category: {categories_summary}")

                if 'regional_performance' in insights:
                    regions = insights['regional_performance'][:5]
                    regions_summary = ", ".join([f"{reg['region']}: ${reg['total_revenue']:,.2f}" for reg in regions])
                    context_parts.append(f"Regional Performance: {regions_summary}")

                if 'total_revenue' in insights:
                    context_parts.append(f"Total Revenue: ${insights['total_revenue']:,.2f}")
                    context_parts.append(f"Average Transaction: ${insights['average_transaction']:,.2f}")
                    context_parts.append(f"Total Transactions: {insights['total_transactions']:,}")

                if 'monthly_trends' in insights:
                    recent_months = insights['monthly_trends'][-3:]  # Last 3 months
                    trends_summary = ", ".join([f"{month['month']}: ${month['revenue']:,.2f}" for month in recent_months])
                    context_parts.append(f"Recent Monthly Revenue: {trends_summary}")

                if 'monthly_growth_rate' in insights:
                    growth = insights['monthly_growth_rate']
                    context_parts.append(f"Monthly Growth Rate: {growth:+.1f}%")

                # Add AI-generated insights
                if 'trends' in insights:
                    context_parts.append(f"Identified Trends: {', '.join(insights['trends'])}")
                if 'anomalies' in insights:
                    context_parts.append(f"Anomalies: {', '.join(insights['anomalies'])}")
                if 'predictions' in insights:
                    context_parts.append(f"Predictions: {', '.join(insights['predictions'])}")

                context = "\n\n".join(context_parts)

                prompt = f"""
                You are an AI business analyst. Answer the user's question using the provided computed data and insights. 
                Give direct, specific answers with actual numbers when available. Don't suggest how to calculate things - use the computed results.

                Available Data:
                {context}

                Question: {state['question']}

                Instructions:
                - Use specific numbers and names from the computed data
                - Be concise and direct
                - If the exact answer isn't in the data, say so and provide the closest relevant information
                - Format currency values clearly (e.g., $1,234.56)
                - Don't suggest calculations or code - use the provided computed results
                """

                response = await self.client.chat.completions.create(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
                answer = response.choices[0].message.content.strip()
                state["answer"] = answer
                logger.info("Generated chat answer", file_id=state["file_id"], question=state["question"])
                return state

            # Add node
            workflow.add_node("generate_answer", generate_answer)
            workflow.set_entry_point("generate_answer")
            workflow.add_edge("generate_answer", END)

            # Compile and run
            graph = workflow.compile()
            initial_state = ChatState(
                file_id=file_id,
                user_id=user_id,
                question=question,
                analysis_data=analysis_data,
                chat_history=chat_history,
                answer=""
            )
            result = await graph.ainvoke(initial_state)

            return result["answer"]
        except Exception as e:
            logger.error("Failed to process chat", error=str(e), file_id=file_id, user_id=user_id)
            raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        if not chat_history:
            return "No previous conversation."
        return "\n".join([f"Q: {msg['question']}\nA: {msg['answer']}" for msg in chat_history[-3:]])  # Last 3 exchanges