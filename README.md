# Review and Feedback Microservice

## Overview
This microservice handles customer feedback and reviews for consumed entities. It allows customers to submit initial ratings and comments, as well as update their previously submitted feedback.

## Team Members
- Lev: Main implementation (API endpoints, business logic)
- Thomas: Initial setup + deployment/Docker configuration
- Olivia: Database schema design, UML diagrams, Testing

## User Stories

### 1. Submit Initial Feedback
**As a customer**, I want to submit my initial rating and written comment for a consumed entity so that I can officially record and share my experience with the system.

**Acceptance Criteria:**
- Functional: Logged-in customers can submit feedback with User ID, Entity ID, 1-5 star rating, and comment
- Non-functional (Usability): API endpoint requires maximum of three core fields for feedback submission

### 2. Update Existing Feedback
**As a customer**, I want to edit the rating or comment of feedback I previously submitted so that I can update my feedback if my experience with the entity changes over time.

**Acceptance Criteria:**
- Functional: Customers can update their own feedback with verification of User ID and modification timestamp
- Non-functional (Securability): Clear audit logs of all modifications including before/after states

## Technology Stack
- **Language**: Python 3.9
- **Framework**: Flask 3.0.0
- **CORS**: Flask-Cors 4.0.0
- **Environment**: python-dotenv 1.0.0

## Getting Started

### Prerequisites
- Docker installed on your machine
- Python 3.9+ (for local development)

### Installation

#### Using Docker (Recommended)
```bash
# Build the Docker image
docker build -t review-feedback-service .

# Run the container
docker run -p 5005:5005 review-feedback-service
```

#### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Configuration

### Environment Variables
- `PORT`: Server port (default: 5005)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: "http://localhost:5173,http://localhost:5000")

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the microservice.

**Response:**
```json
{
  "message": "Review and Feedback Microservice Online"
}
```

### Submit Feedback (Coming Soon)
```
POST /feedback
```

### Update Feedback (Coming Soon)
```
PUT /feedback/{feedback_id}
```

## Database Schema

### Feedbacks Collection (MongoDB)

![Database Schema](images/database-schema.png)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| _id | ObjectId | Yes | MongoDB auto-generated ID |
| feedbackId | String | Yes | Unique feedback identifier (UUID) |
| userId | String | Yes | User who submitted feedback |
| entityId | String | Yes | Entity being reviewed |
| rating | Integer | Yes | Rating (1-5 stars) |
| comment | Text | No | Optional feedback comment |
| last_modified | DateTime | Yes | Last modification timestamp (UTC) |

## UML Diagrams
(To be created by Olivia)

## Testing
(To be implemented by Olivia)

## Project Structure
```
Review-And-Feedback-Microservice/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # Project documentation
```

## Development Status
- [x] Initial Flask setup
- [x] Docker configuration
- [x] CORS configuration
- [ ] Database schema design
- [ ] API endpoint implementation
- [ ] Authentication/Authorization
- [ ] Audit logging
- [ ] UML diagrams
- [ ] Unit tests
- [ ] Integration tests

## Contributing
Please coordinate with team members before making major changes to shared components.
