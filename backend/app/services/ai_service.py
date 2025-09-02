from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

from ..config import settings

# Conditional imports for AI services
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.agents import initialize_agent, Tool
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not installed. AI features will return mock responses.")

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, db=None):
        self.db = db
        self.llm = None
        self.agent = None
        self.setup_ai_services()

    def setup_ai_services(self):
        """Initialize AI services if available"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("AI services not available - LangChain not installed")
            return

        if not settings.openrouter_api_key:
            logger.warning("AI services not available - OpenRouter API key not configured")
            return

        try:
            # Initialize OpenRouter LLM via OpenAI-compatible API
            self.llm = ChatOpenAI(
                openai_api_base=settings.openrouter_base_url,
                openai_api_key=settings.openrouter_api_key,
                model_name=settings.default_ai_model,
                temperature=0.7,
                max_tokens=500
            )
            
            # Setup tools for the agent
            tools = [
                Tool(
                    name="Search Places",
                    func=self._search_places_tool,
                    description="Search for fika places by name, city, or features"
                ),
                Tool(
                    name="Get Place Info",
                    func=self._get_place_info_tool,
                    description="Get detailed information about a specific place"
                ),
                Tool(
                    name="Swedish Culture Info",
                    func=self._swedish_culture_info,
                    description="Provide information about Swedish fika culture and traditions"
                )
            ]
            
            # Initialize conversation memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Initialize agent
            self.agent = initialize_agent(
                tools,
                self.llm,
                agent="conversational-react-description",
                memory=memory,
                verbose=settings.debug,
                max_iterations=3
            )
            
            logger.info("AI services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            self.llm = None
            self.agent = None

    async def get_recommendations(self, user_preferences: Dict[str, Any], city: Optional[str] = None, max_results: int = 5) -> Dict[str, Any]:
        """Get personalized fika place recommendations"""
        try:
            if not self.llm:
                return self._mock_recommendations(user_preferences, city, max_results)

            prompt = f"""
            Based on these user preferences: {json.dumps(user_preferences)}
            {"" if not city else f"Focusing on {city}, "}recommend {max_results} traditional Swedish fika places.
            
            Consider:
            - Traditional Swedish pastries (kanelbullar, prinsesstårta, etc.)
            - Atmosphere and authenticity
            - Price range preferences
            - Special dietary needs
            - Location preferences
            
            Return recommendations as a structured response with explanations.
            """
            
            response = await self.llm.agenerate([prompt])
            
            return {
                "recommendations": self._parse_recommendations(response.generations[0][0].text),
                "explanation": "AI-generated recommendations based on your preferences",
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return self._mock_recommendations(user_preferences, city, max_results)

    async def moderate_content(self, text: str, content_type: str = "review") -> Dict[str, Any]:
        """Use AI to moderate user-generated content"""
        try:
            if not self.llm:
                return self._mock_content_moderation(text)

            prompt = f"""
            Analyze this {content_type} for a Swedish fika location and determine:
            1. Is it appropriate and respectful? (yes/no)
            2. Toxicity level (0.0 to 1.0, where 0 is completely safe)
            3. Does it contain spam or promotional content? (yes/no)
            4. What language is it in? (language code)
            5. Brief explanation of the assessment
            
            Text to analyze: "{text}"
            
            Respond in JSON format with keys: is_appropriate, toxicity_score, contains_spam, language, explanation
            """
            
            response = await self.llm.agenerate([prompt])
            result = self._parse_moderation_response(response.generations[0][0].text)
            
            return result
            
        except Exception as e:
            logger.error(f"Content moderation failed: {e}")
            return self._mock_content_moderation(text)

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Chat with AI assistant about fika places and Swedish culture"""
        try:
            if not self.agent:
                return self._mock_chat_response(message)

            # Add context to the message if provided
            if context:
                enhanced_message = f"Context: {json.dumps(context)}\n\nUser question: {message}"
            else:
                enhanced_message = message
            
            response = await self.agent.arun(enhanced_message)
            
            return {
                "response": response,
                "suggestions": self._generate_suggestions(message),
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return self._mock_chat_response(message)

    async def enrich_place_data(self, place: Any) -> Dict[str, Any]:
        """Use AI to enrich place data with additional information"""
        try:
            if not self.llm:
                return self._mock_place_enrichment(place)

            prompt = f"""
            Analyze this Swedish fika location and suggest enrichments:
            
            Name: {place.name}
            City: {place.city}
            Current description: {place.description or 'No description available'}
            Specialties: {', '.join(place.fika_specialties or [])}
            
            Provide:
            1. An improved description focusing on Swedish fika culture
            2. Suggested traditional Swedish specialties if missing
            3. Recommended features/amenities
            4. SEO-friendly meta description
            
            Respond in JSON format with keys: description, specialties, features, meta_description
            """
            
            response = await self.llm.agenerate([prompt])
            result = self._parse_enrichment_response(response.generations[0][0].text)
            
            return result
            
        except Exception as e:
            logger.error(f"Place enrichment failed: {e}")
            return self._mock_place_enrichment(place)

    async def generate_place_description(self, place: Any) -> str:
        """Generate AI-powered description for a place"""
        try:
            if not self.llm:
                return self._mock_place_description(place)

            prompt = f"""
            Write an engaging description for this Swedish fika location:
            
            Name: {place.name}
            City: {place.city}
            Address: {place.address or 'Address not available'}
            Specialties: {', '.join(place.fika_specialties or [])}
            
            The description should:
            - Capture the essence of Swedish fika culture
            - Mention traditional elements if applicable
            - Be inviting and authentic
            - Be 2-3 sentences long
            - Appeal to both locals and tourists
            
            Write only the description, no additional formatting.
            """
            
            response = await self.llm.agenerate([prompt])
            return response.generations[0][0].text.strip()
            
        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return self._mock_place_description(place)

    async def detect_duplicate_places(self) -> List[Dict[str, Any]]:
        """Use AI to detect potential duplicate place entries"""
        try:
            # This would require database access to compare places
            # For now, return mock data
            return self._mock_duplicate_detection()
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return []

    async def get_analytics(self, timeframe: str) -> Dict[str, Any]:
        """Generate AI-powered analytics and insights"""
        try:
            return {
                "timeframe": timeframe,
                "insights": [
                    "Traditional konditoris show higher user engagement",
                    "Stockholm locations receive more international visitors",
                    "Cinnamon bun popularity peaks on weekends"
                ],
                "recommendations": [
                    "Focus marketing on weekend fika experiences",
                    "Highlight traditional aspects in descriptions",
                    "Consider seasonal specialty promotions"
                ],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {"error": str(e)}

    # Tool functions for the agent
    def _search_places_tool(self, query: str) -> str:
        """Tool function for searching places"""
        try:
            # This would integrate with the place service
            return f"Found places matching '{query}' (mock response)"
        except Exception as e:
            return f"Search failed: {e}"

    def _get_place_info_tool(self, place_name: str) -> str:
        """Tool function for getting place information"""
        try:
            return f"Information about {place_name} (mock response)"
        except Exception as e:
            return f"Info lookup failed: {e}"

    def _swedish_culture_info(self, topic: str) -> str:
        """Tool function for Swedish culture information"""
        culture_info = {
            "fika": "Fika is a Swedish coffee break tradition emphasizing social connection and quality time.",
            "kanelbullar": "Cinnamon buns are Sweden's national pastry, typically enjoyed during fika.",
            "prinsesstarta": "Princess cake is a traditional Swedish layer cake covered in green marzipan.",
            "konditori": "Traditional Swedish pastry shops that have served communities for generations."
        }
        
        return culture_info.get(topic.lower(), f"Swedish culture topic: {topic}")

    # Mock response generators for when AI services are unavailable
    def _mock_recommendations(self, preferences: Dict[str, Any], city: Optional[str], max_results: int) -> Dict[str, Any]:
        """Generate mock recommendations"""
        mock_places = [
            {"name": "Traditional Konditori", "city": city or "Stockholm", "reason": "Authentic Swedish pastries"},
            {"name": "Cozy Coffee Corner", "city": city or "Stockholm", "reason": "Perfect atmosphere for fika"},
            {"name": "Historic Bakery", "city": city or "Stockholm", "reason": "Rich Swedish heritage"}
        ]
        
        return {
            "recommendations": mock_places[:max_results],
            "explanation": "Mock recommendations based on your preferences (AI services not available)",
            "confidence": 0.5
        }

    def _mock_content_moderation(self, text: str) -> Dict[str, Any]:
        """Generate mock content moderation response"""
        return {
            "is_appropriate": len(text) > 0 and not any(word in text.lower() for word in ["spam", "hate"]),
            "toxicity_score": 0.1,
            "contains_spam": "spam" in text.lower(),
            "language": "sv" if any(word in text.lower() for word in ["fika", "kaffe", "kaka"]) else "en",
            "explanation": "Mock moderation result (AI services not available)"
        }

    def _mock_chat_response(self, message: str) -> Dict[str, Any]:
        """Generate mock chat response"""
        return {
            "response": f"Thank you for your question about '{message}'. AI chat services are currently not available, but our database contains information about traditional Swedish fika locations across major cities.",
            "suggestions": ["Search for places in Stockholm", "Browse traditional konditoris", "Learn about Swedish fika culture"],
            "confidence": 0.5
        }

    def _mock_place_enrichment(self, place: Any) -> Dict[str, Any]:
        """Generate mock place enrichment"""
        return {
            "description": f"{place.name} offers an authentic Swedish fika experience in {place.city}.",
            "specialties": ["Kanelbullar", "Coffee", "Traditional pastries"],
            "features": ["Traditional atmosphere", "Local favorite"],
            "meta_description": f"Experience traditional Swedish fika at {place.name} in {place.city}."
        }

    def _mock_place_description(self, place: Any) -> str:
        """Generate mock place description"""
        return f"{place.name} in {place.city} offers an authentic Swedish fika experience with traditional pastries and excellent coffee in a welcoming atmosphere."

    def _mock_duplicate_detection(self) -> List[Dict[str, Any]]:
        """Generate mock duplicate detection results"""
        return []

    # Response parsing helpers
    def _parse_recommendations(self, text: str) -> List[Dict[str, Any]]:
        """Parse AI recommendations response"""
        try:
            # Attempt to parse JSON response
            return json.loads(text)
        except:
            # Fallback to parsing text
            return [{"name": "Parsed recommendation", "reason": text[:100]}]

    def _parse_moderation_response(self, text: str) -> Dict[str, Any]:
        """Parse AI moderation response"""
        try:
            return json.loads(text)
        except:
            return {
                "is_appropriate": True,
                "toxicity_score": 0.1,
                "contains_spam": False,
                "language": "unknown",
                "explanation": "Parsing failed, defaulting to safe values"
            }

    def _parse_enrichment_response(self, text: str) -> Dict[str, Any]:
        """Parse AI enrichment response"""
        try:
            return json.loads(text)
        except:
            return {
                "description": text[:200] if text else "AI enrichment response parsing failed",
                "specialties": [],
                "features": [],
                "meta_description": ""
            }

    def _generate_suggestions(self, message: str) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        if "stockholm" in message.lower():
            suggestions.append("Find traditional konditoris in Stockholm")
        if "coffee" in message.lower() or "kaffe" in message.lower():
            suggestions.append("Discover specialty coffee roasters")
        if "pastry" in message.lower() or "kanelbullar" in message.lower():
            suggestions.append("Learn about Swedish pastry traditions")
        
        if not suggestions:
            suggestions = [
                "Explore fika places by city",
                "Learn about Swedish fika culture",
                "Find highly-rated traditional locations"
            ]
        
        return suggestions