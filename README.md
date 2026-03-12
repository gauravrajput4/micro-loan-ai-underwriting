# Micro Loan Application

An AI-powered personal loan underwriting system for students, unemployed individuals, and administrators.

## Features

- **Multi-user Support**: Students, unemployed individuals, and administrators
- **AI-Powered Loan Assessment**: Machine learning-based loan approval system
- **Bank Statement Analysis**: Upload and analyze bank statements
- **EMI Calculator**: Calculate loan EMI with different parameters
- **Admin Dashboard**: Comprehensive admin panel for loan management
- **Real-time Analytics**: Dashboard with loan statistics and trends

## Tech Stack

### Frontend
- React 19 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Motion for animations
- React Router for navigation
- Recharts for data visualization

### Backend
- FastAPI (Python)
- MongoDB for database
- Machine Learning with scikit-learn
- JWT authentication
- CORS enabled for frontend integration

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Micro Loan"
   ```

2. **Start both servers**
   ```bash
   ./start.sh
   ```

   This script will:
   - Set up Python virtual environment
   - Install backend dependencies
   - Install frontend dependencies
   - Start both servers concurrently

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

If you prefer to run servers manually:

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## User Types & Features

### Students
- Apply for educational loans
- Upload bank statements for analysis
- View loan application status
- Calculate EMI for different loan amounts

### Unemployed Individuals
- Apply for personal loans
- Upload financial documents
- Access loan recommendations
- Track application progress

### Administrators
- View comprehensive dashboard
- Manage loan applications
- Review user applications
- Access system analytics

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Loan Management
- `POST /api/loan/apply` - Submit loan application
- `GET /api/loan/applications` - Get user applications
- `POST /api/loan/calculate-emi` - Calculate EMI

### Dashboard
- `GET /api/dashboard/admin-dashboard` - Admin analytics

### File Upload
- `POST /api/upload/bank-statement` - Upload bank statement

## Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
MONGODB_URL=mongodb://localhost:27017/microloan
OPENAI_API_KEY=your-openai-key-here
```

## Default User Accounts

For testing purposes, you can create accounts with these user types:
- **Student**: Select "Student" during registration
- **Unemployed**: Select "Unemployed" during registration  
- **Admin**: Select "Admin" during registration

## Development

### Frontend Development
```bash
cd frontend
npm run dev     # Start development server
npm run build   # Build for production
npm run lint    # Run TypeScript checks
```

### Backend Development
```bash
cd backend
python main.py  # Start development server
```

## Project Structure

```
Micro Loan/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── lib/           # Utilities
│   └── package.json
├── backend/
│   ├── routes/            # API routes
│   ├── services/          # Business logic
│   ├── database/          # Database connections
│   ├── ml/               # Machine learning models
│   └── main.py           # FastAPI app
└── start.sh              # Startup script
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
