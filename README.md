# TailorTalk 🚀
### Conversational AI Calendar Booking Agent

TailorTalk is an intelligent conversational AI agent that seamlessly integrates with Google Calendar to help users book appointments through natural language conversations. Built with modern AI frameworks and a user-friendly interface, it provides an intuitive way to schedule meetings without the hassle of traditional booking systems.

## ✨ Features

- **Natural Language Processing**: Understands user intent through conversational AI
- **Google Calendar Integration**: Real-time calendar availability checking and booking
- **Intelligent Scheduling**: Suggests optimal time slots based on availability
- **Conversational Flow**: Engaging back-and-forth dialogue for seamless user experience
- **Real-time Confirmation**: Instant booking confirmation with calendar updates
- **Flexible Time Handling**: Supports various date/time formats and natural language expressions

## 🛠 Technical Stack

- **Backend**: Python with FastAPI
- **AI Framework**: LangGraph/LangChain for conversational AI
- **Frontend**: Streamlit for interactive chat interface
- **LLM**: Gemini/Grok API for natural language understanding
- **Calendar API**: Google Calendar API with Service Account authentication
- **Deployment**: Railway/Render/Fly.io

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Service Account with Google Calendar API access
- LLM API key (Gemini, Grok, etc.)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/tailortalk.git
cd tailortalk
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
# Google Calendar API
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/your/service-account.json
CALENDAR_ID=your-calendar-id@gmail.com

# LLM API Configuration
GEMINI_API_KEY=your-gemini-api-key
# OR
GROK_API_KEY=your-grok-api-key

# FastAPI Configuration
HOST=0.0.0.0
PORT=8000
```

### 4. Google Calendar Setup
1. Create a Google Cloud Project
2. Enable Google Calendar API
3. Create a Service Account
4. Download the service account JSON file
5. Share your calendar with the service account email
6. Update the `GOOGLE_SERVICE_ACCOUNT_FILE` path in `.env`

### 5. Run the Application

#### Start the Backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Start the Frontend
```bash
streamlit run streamlit_app.py
```



## 🤖 How It Works

1. **User Input**: User describes their booking requirements in natural language
2. **Intent Recognition**: AI agent processes the request and identifies booking intent
3. **Calendar Check**: Agent queries Google Calendar for availability
4. **Suggestion**: Agent suggests suitable time slots based on availability
5. **Confirmation**: User confirms the booking details
6. **Booking**: Agent creates the calendar event and provides confirmation

## 💬 Example Conversations

```
User: "I need to schedule a meeting with John next Tuesday afternoon"
Agent: "I'd be happy to help you schedule that meeting! Let me check your availability for next Tuesday afternoon. I see you have these open slots:
- 2:00 PM - 3:00 PM
- 3:30 PM - 4:30 PM
- 4:00 PM - 5:00 PM

Which time works best for you?"

User: "3:30 PM sounds perfect"
Agent: "Great! I'll book 'Meeting with John' for Tuesday, [date] at 3:30 PM - 4:30 PM. The event has been added to your calendar. Is there anything else you'd like to add to this meeting?"
```

## 🛠 API Endpoints

### FastAPI Backend Endpoints

- `POST /chat` - Main chat endpoint for conversation
- `GET /calendar/availability` - Check calendar availability
- `POST /calendar/book` - Book a new appointment
- `GET /calendar/events` - Retrieve calendar events
- `DELETE /calendar/events/{event_id}` - Cancel an appointment

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to Google service account JSON | Yes |
| `CALENDAR_ID` | Google Calendar ID | Yes |
| `GEMINI_API_KEY` | Gemini API key | Yes* |
| `GROK_API_KEY` | Grok API key | Yes* |
| `HOST` | Server host | No (default: 0.0.0.0) |
| `PORT` | Server port | No (default: 8000) |

*One LLM API key is required

## 📈 Features Roadmap

- [ ] Multi-language support
- [ ] Meeting reminders
- [ ] Recurring appointments
- [ ] Meeting room booking
- [ ] Email notifications
- [ ] Calendar conflict resolution
- [ ] Time zone handling
- [ ] Voice input support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/vaibhav-bhosale1/tailortalk/issues) page
2. Create a new issue with detailed description
3. Contact the maintainers

## 🙏 Acknowledgments

- Google Calendar API for seamless integration
- LangGraph/LangChain for conversational AI framework
- Streamlit for the intuitive frontend
- FastAPI for the robust backend architecture

---

## 📞 Live Demo- Still working on it

🌐 **Streamlit App**: [https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)

📚 **API Documentation**: [https://your-api-url.com/docs](https://your-api-url.com/docs)

💻 **GitHub Repository**: [https://github.com/yourusername/tailortalk](https://github.com/vaibhav-bhosale1/TailorTalk_Agent)

