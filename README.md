# Network+ & Security+ Certification Exam Web Application

A Python web application built with Flask that provides a comprehensive exam for Network+ and Security+ cybersecurity certification preparation. Test your knowledge with randomly selected questions and get instant feedback with pass/fail results.

## Features

- 📚 **Comprehensive Coverage**: 150 exam questions covering Network+ and Security+ topics
- 🎲 **Randomized Exams**: Each exam randomly selects 20 questions for variety
- ✅ **Instant Feedback**: Get immediate results with detailed answer review
- 📊 **Scoring System**: Pass/fail based on 70% threshold
- 🎨 **Modern UI**: Beautiful, responsive design with gradient styling
- 🔒 **Session-Based**: Secure exam sessions with Flask sessions

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Click "Start Exam" to begin your test

## How It Works

1. **Start Page**: View exam information and requirements
2. **Exam Page**: Answer 20 randomly selected questions from 150 available
3. **Results Page**: See your score, pass/fail status, and detailed review of all answers

## Exam Details

- **Total Questions Pool**: 150 questions
- **Questions Per Exam**: 20 randomly selected
- **Passing Score**: 70%
- **Topics Covered**: 
  - Network protocols and ports
  - Network security concepts
  - Encryption and authentication
  - OSI model and networking fundamentals
  - Cybersecurity threats and defenses
  - Wireless security (802.11 standards, WEP/WPA/WPA2/WPA3)
  - Network troubleshooting
  - Routing and switching (RIP, OSPF, BGP, EIGRP)
  - Network access control (NAC, 802.1X)
  - VPN and remote access
  - Security frameworks (CIA, RBAC, NIST)
  - Physical and logical security
  - Malware types and attacks
  - Compliance and regulations (GDPR, SOX, HIPAA)
  - Industrial control systems (SCADA, ICS)
  - IPv6 addressing and transition technologies

## Security Note

**Important**: Change the `secret_key` in `app.py` before deploying to production:

```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

For production, use a strong, randomly generated secret key.

## Customization

### Adding More Questions

Edit the `QUESTIONS` list in `app.py` to add more exam questions:

```python
{
    "id": 26,
    "question": "Your question here?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct": 0,  # Index of correct answer (0-3)
    "topic": "Network+"
}
```

### Changing Exam Size

Modify the `EXAM_SIZE` variable in `app.py`:

```python
EXAM_SIZE = 20  # Change to desired number of questions
```

### Adjusting Pass Score

Change the passing threshold in the `results` function in `app.py`:

```python
passed = score >= 80  # Change 70 to desired percentage
```

## Project Structure

```
CNA/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── index.html        # Welcome/start page
│   ├── exam.html         # Exam interface
│   └── results.html      # Results page
└── static/               # Static assets
    └── style.css         # Stylesheet
```

## Technologies Used

- **Flask**: Web framework
- **Python**: Programming language
- **HTML/CSS**: Frontend design
- **Sessions**: User session management

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to add more questions, improve the UI, or enhance functionality!

## Support

For issues or questions, please create an issue in the repository.

